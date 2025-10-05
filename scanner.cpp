#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <thread>
#include <chrono>
#include <sstream>
#include <regex>
#include <algorithm>
#include <cctype>

using json = nlohmann::json;
using namespace std;

// Helper function to convert string to lowercase
string toLower(const string& str) {
    string result = str;
    transform(result.begin(), result.end(), result.begin(), ::tolower);
    return result;
}

class OSINTFramework {
private:
    string user_agent;
    
    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, string* response) {
        size_t total_size = size * nmemb;
        response->append((char*)contents, total_size);
        return total_size;
    }
    
    // Simple struct to hold request results
    struct RequestResult {
        long status_code;
        string response;
    };
    
    RequestResult makeRequest(const string& url, const vector<string>& headers = {}) {
        CURL* curl;
        CURLcode res;
        string response;
        long status_code = 0;
        
        curl = curl_easy_init();
        
        if(curl) {
            curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
            curl_easy_setopt(curl, CURLOPT_USERAGENT, user_agent.c_str());
            curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
            curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30L);
            curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);
            
            struct curl_slist* chunk = NULL;
            for(const auto& header : headers) {
                chunk = curl_slist_append(chunk, header.c_str());
            }
            if(chunk) {
                curl_easy_setopt(curl, CURLOPT_HTTPHEADER, chunk);
            }
            
            res = curl_easy_perform(curl);
            
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status_code);
            
            if(chunk) {
                curl_slist_free_all(chunk);
            }
            
            if(res != CURLE_OK) {
                cerr << "Request failed: " << curl_easy_strerror(res) << endl;
            }
            
            curl_easy_cleanup(curl);
        }
        
        this_thread::sleep_for(chrono::milliseconds(500));
        
        RequestResult result;
        result.status_code = status_code;
        result.response = response;
        return result;
    }
    
    json parseJSON(const string& response) {
        try {
            return json::parse(response);
        } catch (const exception& e) {
            return json();
        }
    }

public:
    OSINTFramework() : user_agent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36") {
        curl_global_init(CURL_GLOBAL_DEFAULT);
    }
    
    ~OSINTFramework() {
        curl_global_cleanup();
    }

    // wTnk - Username search across multiple platforms
    void usernameSearch(const string& username) {
        cout << "\n🔍 Searching for username: " << username << endl;

        map<string, string> platforms = {
            {"Reddit", "https://www.reddit.com/user/" + username + "/about.json"},
            {"GitHub", "https://api.github.com/users/" + username},
            {"GitLab", "https://gitlab.com/api/v4/users?username=" + username},
            {"Keybase", "https://keybase.io/_/api/1.0/user/lookup.json?usernames=" + username}
        };

        for(map<string, string>::const_iterator it = platforms.begin(); it != platforms.end(); ++it) {
            cout << "📱 Checking " << it->first << "... ";
            RequestResult result = makeRequest(it->second);
            bool exists = (result.status_code == 200);
            if (exists) {
                cout << "✅ FOUND: " + it->second << endl;
                json data = parseJSON(result.response);
                if (!data.empty()) {
                    if (it->first == "GitHub") {
                        cout << "  👤 Name: " << data.value("name", "N/A") << endl;
                        cout << "  📊 Repos: " << data.value("public_repos", 0) << endl;
                        cout << "  👥 Followers: " << data.value("followers", 0) << endl;
                    } else if (it->first == "Reddit") {
                        if (data.find("data") != data.end()) {
                            auto user_data = data["data"];
                            cout << "  ⭐ Karma: " << user_data.value("total_karma", 0) << endl;
                            cout << "  🕒 Created: " << user_data.value("created_utc", 0) << endl;
                        }
                    } else if (it->first == "GitLab") {
                        if (data.is_array() && !data.empty()) {
                            auto user_data = data[0];
                            cout << "  👤 Name: " << user_data.value("name", "N/A") << endl;
                        }
                    }
                }
            } else {
                cout << "❌ NOT FOUND" << endl;
            }
        }
    }

    // dLkp - DNS lookup
    void dnsLookup(const string& domain) {
        cout << "\n🌐 DNS Lookup for: " << domain << endl;
        string url = "https://dns.google/resolve?name=" + domain + "&type=A";
        RequestResult result = makeRequest(url);
        json data = parseJSON(result.response);
        
        if(!data.empty() && data.find("Answer") != data.end()) {
            for(const auto& answer : data["Answer"]) {
                cout << "📍 " << answer.value("type", 0) 
                     << " | " << answer.value("data", "N/A") << endl;
            }
        }
    }

    // wBck - Wayback Machine
    void waybackUrls(const string& domain) {
        cout << "\n🕰️ Wayback Machine for: " << domain << endl;
        string url = "http://web.archive.org/cdx/search/cdx?url=" + domain + "/*&output=json&limit=5";
        RequestResult result = makeRequest(url);
        
        try {
            json data = json::parse(result.response);
            if(data.is_array() && data.size() > 1) {
                cout << "📄 Found " << data.size()-1 << " archived URLs" << endl;
                for(size_t i = 1; i < (data.size() < 6 ? data.size() : 6); i++) {
                    if(data[i].is_array() && data[i].size() > 2) {
                        cout << "🔗 " << data[i][2] << endl;
                    }
                }
            }
        } catch (...) {
            cout << "❌ Failed to parse Wayback data" << endl;
        }
    }

    // gHub - GitHub info
    void githubInfo(const string& username) {
        cout << "\n💻 GitHub Info for: " << username << endl;
        string url = "https://api.github.com/users/" + username;
        RequestResult result = makeRequest(url);
        json data = parseJSON(result.response);
        
        if(!data.empty()) {
            cout << "👤 Name: " << data.value("name", "N/A") << endl;
            cout << "📊 Repos: " << data.value("public_repos", 0) << endl;
            cout << "👥 Followers: " << data.value("followers", 0) << endl;
            cout << "🏢 Company: " << data.value("company", "N/A") << endl;
            cout << "📍 Location: " << data.value("location", "N/A") << endl;
        } else {
            cout << "❌ User not found" << endl;
        }
    }

    // rDdt - Reddit info
    void redditInfo(const string& username) {
        cout << "\n📱 Reddit Info for: " << username << endl;
        string url = "https://www.reddit.com/user/" + username + "/about.json";
        RequestResult result = makeRequest(url);
        json data = parseJSON(result.response);
        
        if(!data.empty() && data.find("data") != data.end()) {
            auto user_data = data["data"];
            cout << "⭐ Karma: " << user_data.value("total_karma", 0) << endl;
            cout << "🕒 Created: " << user_data.value("created_utc", 0) << endl;
        } else {
            cout << "❌ User not found" << endl;
        }
    }

    // iPlc - IP location
    void ipLocation(const string& ip) {
        cout << "\n📍 IP Location for: " << ip << endl;
        string url = "http://ipapi.co/" + ip + "/json/";
        RequestResult result = makeRequest(url);
        json data = parseJSON(result.response);
        
        if(!data.empty() && data.find("error") == data.end()) {
            cout << "🏙️ City: " << data.value("city", "N/A") << endl;
            cout << "🌍 Country: " << data.value("country_name", "N/A") << endl;
            cout << "🏢 ISP: " << data.value("org", "N/A") << endl;
        } else {
            cout << "❌ IP not found" << endl;
        }
    }

    // wHis - WHOIS lookup
    void whoisLookup(const string& domain) {
        cout << "\n🔍 WHOIS Lookup for: " << domain << endl;
        string url = "https://www.whois.com/whois/" + domain;
        RequestResult result = makeRequest(url);
        
        regex domain_regex("Domain Name: ([^\\n]+)");
        regex created_regex("Creation Date: ([^\\n]+)");
        
        smatch match;
        if(regex_search(result.response, match, domain_regex)) {
            cout << "🏷️ Domain: " << match[1] << endl;
        }
        if(regex_search(result.response, match, created_regex)) {
            cout << "📅 Created: " << match[1] << endl;
        }
    }

    // sSll - SSL certificate info
    void sslInfo(const string& domain) {
        cout << "\n🔒 SSL Certificates for: " << domain << endl;
        string url = "https://crt.sh/?q=" + domain + "&output=json";
        RequestResult result = makeRequest(url);
        
        try {
            json data = json::parse(result.response);
            if(data.is_array() && !data.empty()) {
                cout << "📜 Found " << data.size() << " certificates" << endl;
                auto cert = data[0];
                cout << "📛 Common Name: " << cert.value("common_name", "N/A") << endl;
            }
        } catch (...) {
            cout << "❌ No certificate data" << endl;
        }
    }

    // eMbp - Email breach check
    void emailBreach(const string& email) {
        cout << "\n🛡️ Breach Check for: " << email << endl;
        string url = "https://haveibeenpwned.com/api/v3/breachedaccount/" + email;
        vector<string> headers;
        headers.push_back("User-Agent: OSINT-Tool");
        RequestResult result = makeRequest(url, headers);
        json data = parseJSON(result.response);
        
        if(data.is_array() && !data.empty()) {
            cout << "🚨 Breaches found: " << data.size() << endl;
            size_t limit = data.size() < 3 ? data.size() : 3;
            for(size_t i = 0; i < limit; i++) {
                cout << "💥 " << data[i].value("Name", "N/A") << endl;
            }
        } else {
            cout << "✅ No breaches found" << endl;
        }
    }

    // bTcn - Bitcoin address info
    void bitcoinInfo(const string& address) {
        cout << "\n₿ Bitcoin Address: " << address << endl;
        string url = "https://blockstream.info/api/address/" + address;
        RequestResult result = makeRequest(url);
        json data = parseJSON(result.response);
        
        if(!data.empty()) {
            json chain_stats = data.value("chain_stats", json::object());
            cout << "💰 Transactions: " << chain_stats.value("tx_count", 0) << endl;
        } else {
            cout << "❌ Address not found" << endl;
        }
    }

    // hNws - Hacker News user
    void hackerNewsUser(const string& username) {
        cout << "\n👨‍💻 Hacker News User: " << username << endl;
        string url = "https://hacker-news.firebaseio.com/v0/user/" + username + ".json";
        RequestResult result = makeRequest(url);
        json data = parseJSON(result.response);
        
        if(!data.empty()) {
            cout << "⭐ Karma: " << data.value("karma", 0) << endl;
        } else {
            cout << "❌ User not found" << endl;
        }
    }

    // sOvf - Stack Overflow user
    void stackOverflowUser(const string& user_id) {
        cout << "\n💼 Stack Overflow User ID: " << user_id << endl;
        string url = "https://api.stackexchange.com/2.3/users/" + user_id + "?site=stackoverflow";
        RequestResult result = makeRequest(url);
        json data = parseJSON(result.response);
        
        if(!data.empty() && data.find("items") != data.end() && !data["items"].empty()) {
            auto user = data["items"][0];
            cout << "⭐ Reputation: " << user.value("reputation", 0) << endl;
        } else {
            cout << "❌ User not found" << endl;
        }
    }

    // fScn - Full domain scan
    void fullDomainScan(const string& domain) {
        cout << "\n🔍 FULL DOMAIN SCAN: " << domain << endl;
        cout << "═══════════════════════════════════════════════════" << endl;
        
        dnsLookup(domain);
        whoisLookup(domain);
        sslInfo(domain);
        waybackUrls(domain);
        
        cout << "═══════════════════════════════════════════════════" << endl;
    }

    // aScn - All username search
    void allUsernameSearch(const string& username) {
        cout << "\n👤 COMPREHENSIVE USERNAME SEARCH: " << username << endl;
        cout << "═══════════════════════════════════════════════════" << endl;
        
        usernameSearch(username);
        githubInfo(username);
        redditInfo(username);
        hackerNewsUser(username);
        
        cout << "═══════════════════════════════════════════════════" << endl;
    }
};

// Parse command line arguments
void parseCommand(const string& command, OSINTFramework& osint) {
    stringstream ss(command);
    string cmd, param;
    ss >> cmd >> param;

    // Convert command to lowercase for case-insensitive comparison
    string cmdLower = toLower(cmd);

    if (cmdLower == "wtnk" && !param.empty()) {
        osint.usernameSearch(param);
    }
    else if (cmdLower == "dlkp" && !param.empty()) {
        osint.dnsLookup(param);
    }
    else if (cmdLower == "wbck" && !param.empty()) {
        osint.waybackUrls(param);
    }
    else if (cmdLower == "ghub" && !param.empty()) {
        osint.githubInfo(param);
    }
    else if (cmdLower == "rddt" && !param.empty()) {
        osint.redditInfo(param);
    }
    else if (cmdLower == "iplc" && !param.empty()) {
        osint.ipLocation(param);
    }
    else if (cmdLower == "whis" && !param.empty()) {
        osint.whoisLookup(param);
    }
    else if (cmdLower == "ssll" && !param.empty()) {
        osint.sslInfo(param);
    }
    else if (cmdLower == "embp" && !param.empty()) {
        osint.emailBreach(param);
    }
    else if (cmdLower == "btcn" && !param.empty()) {
        osint.bitcoinInfo(param);
    }
    else if (cmdLower == "hnws" && !param.empty()) {
        osint.hackerNewsUser(param);
    }
    else if (cmdLower == "sovf" && !param.empty()) {
        osint.stackOverflowUser(param);
    }
    else if (cmdLower == "fscn" && !param.empty()) {
        osint.fullDomainScan(param);
    }
    else if (cmdLower == "ascn" && !param.empty()) {
        osint.allUsernameSearch(param);
    }
    else if (cmdLower == "help") {
        cout << "\n🛠️ OSINT Commands:" << endl;
        cout << "wTnk + username    - Username search across platforms" << endl;
        cout << "dLkp + domain      - DNS lookup" << endl;
        cout << "wBck + domain      - Wayback Machine URLs" << endl;
        cout << "gHub + username    - GitHub user info" << endl;
        cout << "rDdt + username    - Reddit user info" << endl;
        cout << "iPlc + IP          - IP geolocation" << endl;
        cout << "wHis + domain      - WHOIS lookup" << endl;
        cout << "sSll + domain      - SSL certificate info" << endl;
        cout << "eMbp + email       - Email breach check" << endl;
        cout << "bTcn + address     - Bitcoin address info" << endl;
        cout << "hNws + username    - Hacker News user" << endl;
        cout << "sOvf + userid      - Stack Overflow user" << endl;
        cout << "fScn + domain      - Full domain scan" << endl;
        cout << "aScn + username    - All username checks" << endl;
        cout << "help               - Show this help" << endl;
        cout << "exit               - Exit program" << endl;
    }
    else if (cmdLower == "exit") {
        cout << "👋 Goodbye!" << endl;
        exit(0);
    }
    else {
        cout << "❌ Unknown command. Type 'help' for available commands." << endl;
    }
}

int main(int argc, char* argv[]) {
    OSINTFramework osint;
    
    // Command line mode
    if (argc >= 3) {
        string command = argv[1];
        string target = argv[2];
        parseCommand(command + " " + target, osint);
        return 0;
    }
    
    // Interactive mode
    string command;
    cout << "🕵️ OSINT Tool Ready - Type 'help' for commands" << endl;
    cout << "═══════════════════════════════════════════════════" << endl;

    while (true) {
        cout << "\n> ";
        getline(cin, command);
        
        if (!command.empty()) {
            parseCommand(command, osint);
        }
    }

    return 0;
}