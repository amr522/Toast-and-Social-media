#!/usr/bin/env python3
"""
Test Facebook/Instagram API Token
Tests access permissions and posting capabilities for a Facebook access token.
"""

import requests
import json
from datetime import datetime


class FacebookTokenTester:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.results = {
            "token_valid": False,
            "user_info": None,
            "pages": [],
            "instagram_accounts": [],
            "permissions": [],
            "errors": []
        }
    
    def test_token_validity(self):
        """Check if the token is valid and get basic info."""
        print("=" * 60)
        print("TESTING TOKEN VALIDITY")
        print("=" * 60)
        
        url = f"{self.base_url}/me"
        params = {
            "access_token": self.access_token,
            "fields": "id,name,email"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200 and "id" in data:
                self.results["token_valid"] = True
                self.results["user_info"] = data
                print(f"✅ Token is VALID")
                print(f"   User ID: {data.get('id')}")
                print(f"   Name: {data.get('name')}")
                print(f"   Email: {data.get('email', 'N/A')}")
                return True
            else:
                error_msg = data.get('error', {}).get('message', 'Unknown error')
                self.results["errors"].append(f"Token validation failed: {error_msg}")
                print(f"❌ Token is INVALID: {error_msg}")
                return False
                
        except Exception as e:
            self.results["errors"].append(f"Exception during token validation: {str(e)}")
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_permissions(self):
        """Check what permissions the token has."""
        print("\n" + "=" * 60)
        print("CHECKING PERMISSIONS")
        print("=" * 60)
        
        url = f"{self.base_url}/me/permissions"
        params = {"access_token": self.access_token}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "data" in data:
                granted_permissions = [p["permission"] for p in data["data"] if p["status"] == "granted"]
                self.results["permissions"] = granted_permissions
                
                print(f"✅ Found {len(granted_permissions)} granted permissions:")
                for perm in granted_permissions:
                    print(f"   • {perm}")
                
                # Check for important permissions
                important_perms = {
                    "pages_show_list": "View list of pages",
                    "pages_read_engagement": "Read page engagement",
                    "pages_manage_posts": "Publish posts to pages",
                    "instagram_basic": "Basic Instagram access",
                    "instagram_content_publish": "Publish to Instagram"
                }
                
                print("\n📋 Important Permissions Check:")
                for perm, description in important_perms.items():
                    status = "✅" if perm in granted_permissions else "❌"
                    print(f"   {status} {perm}: {description}")
                
                return granted_permissions
            else:
                print("❌ Could not retrieve permissions")
                return []
                
        except Exception as e:
            error_msg = f"Exception checking permissions: {str(e)}"
            self.results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
            return []
    
    def get_pages(self):
        """Get list of Facebook pages the user manages."""
        print("\n" + "=" * 60)
        print("FETCHING FACEBOOK PAGES")
        print("=" * 60)
        
        url = f"{self.base_url}/me/accounts"
        params = {
            "access_token": self.access_token,
            "fields": "id,name,access_token,tasks,instagram_business_account"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                self.results["pages"] = data["data"]
                print(f"✅ Found {len(data['data'])} page(s):\n")
                
                for i, page in enumerate(data["data"], 1):
                    print(f"   Page {i}:")
                    print(f"   • ID: {page['id']}")
                    print(f"   • Name: {page['name']}")
                    print(f"   • Has Page Token: {'Yes' if 'access_token' in page else 'No'}")
                    
                    if "tasks" in page:
                        print(f"   • Tasks: {', '.join(page['tasks'])}")
                    
                    if "instagram_business_account" in page:
                        ig_id = page["instagram_business_account"]["id"]
                        print(f"   • Connected Instagram ID: {ig_id}")
                        self.results["instagram_accounts"].append({
                            "page_id": page["id"],
                            "page_name": page["name"],
                            "instagram_id": ig_id
                        })
                    else:
                        print(f"   • Instagram: Not connected")
                    print()
                
                return data["data"]
            else:
                print("❌ No pages found or no access to pages")
                return []
                
        except Exception as e:
            error_msg = f"Exception fetching pages: {str(e)}"
            self.results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
            return []
    
    def get_instagram_accounts(self):
        """Get Instagram Business accounts connected to pages."""
        print("\n" + "=" * 60)
        print("FETCHING INSTAGRAM ACCOUNTS")
        print("=" * 60)
        
        if not self.results["instagram_accounts"]:
            print("❌ No Instagram accounts found connected to pages")
            return []
        
        for ig_account in self.results["instagram_accounts"]:
            url = f"{self.base_url}/{ig_account['instagram_id']}"
            params = {
                "access_token": self.access_token,
                "fields": "id,username,name,profile_picture_url,followers_count,media_count"
            }
            
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                if response.status_code == 200:
                    print(f"✅ Instagram Account Details:")
                    print(f"   • ID: {data.get('id')}")
                    print(f"   • Username: @{data.get('username')}")
                    print(f"   • Name: {data.get('name')}")
                    print(f"   • Followers: {data.get('followers_count', 'N/A')}")
                    print(f"   • Posts: {data.get('media_count', 'N/A')}")
                    print(f"   • Connected to Page: {ig_account['page_name']}")
                    
                    ig_account.update(data)
                else:
                    error = data.get('error', {}).get('message', 'Unknown error')
                    print(f"❌ Could not fetch Instagram details: {error}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
        
        return self.results["instagram_accounts"]
    
    def test_facebook_post(self, page_data):
        """Test posting to Facebook page (won't actually post)."""
        print("\n" + "=" * 60)
        print(f"TESTING FACEBOOK POST CAPABILITY: {page_data['name']}")
        print("=" * 60)
        
        # Check if we have ANALYZE or MODERATE tasks (for posting)
        tasks = page_data.get("tasks", [])
        can_post = "ANALYZE" in tasks or "CREATE_CONTENT" in tasks or "MODERATE" in tasks
        
        if can_post:
            print(f"✅ Token has posting permissions for '{page_data['name']}'")
            print(f"   Available tasks: {', '.join(tasks)}")
            print(f"   Would be able to post using page token")
            return True
        else:
            print(f"❌ Token does NOT have posting permissions")
            print(f"   Available tasks: {', '.join(tasks) if tasks else 'None'}")
            return False
    
    def test_instagram_post_capability(self, ig_account):
        """Check if we can post to Instagram."""
        print("\n" + "=" * 60)
        print(f"TESTING INSTAGRAM POST CAPABILITY: @{ig_account.get('username', 'Unknown')}")
        print("=" * 60)
        
        # Check permissions
        has_content_publish = "instagram_content_publish" in self.results["permissions"]
        has_basic = "instagram_basic" in self.results["permissions"]
        
        if has_content_publish:
            print(f"✅ Token has 'instagram_content_publish' permission")
            print(f"   Would be able to create posts and stories")
            return True
        elif has_basic:
            print(f"⚠️  Token has 'instagram_basic' but NOT 'instagram_content_publish'")
            print(f"   Can read data but CANNOT post content")
            return False
        else:
            print(f"❌ Token lacks Instagram posting permissions")
            return False
    
    def generate_report(self):
        """Generate a comprehensive test report."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY REPORT")
        print("=" * 60)
        
        print(f"\n📊 Overall Status:")
        print(f"   Token Valid: {'✅ Yes' if self.results['token_valid'] else '❌ No'}")
        print(f"   Facebook Pages: {len(self.results['pages'])} found")
        print(f"   Instagram Accounts: {len(self.results['instagram_accounts'])} found")
        print(f"   Permissions Granted: {len(self.results['permissions'])}")
        
        if self.results['pages']:
            print(f"\n📄 Facebook Page Access:")
            for page in self.results['pages']:
                tasks = page.get('tasks', [])
                can_post = "ANALYZE" in tasks or "CREATE_CONTENT" in tasks
                status = "✅ Can Post" if can_post else "❌ Read Only"
                print(f"   {status} - {page['name']}")
        
        if self.results['instagram_accounts']:
            has_publish = "instagram_content_publish" in self.results['permissions']
            print(f"\n📷 Instagram Access:")
            for ig in self.results['instagram_accounts']:
                status = "✅ Can Post" if has_publish else "❌ Read Only"
                print(f"   {status} - @{ig.get('username', 'Unknown')}")
        
        if self.results['errors']:
            print(f"\n⚠️  Errors Encountered:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print("\n" + "=" * 60)
        
        return self.results
    
    def run_full_test(self):
        """Run all tests in sequence."""
        print("\n🚀 FACEBOOK/INSTAGRAM TOKEN TEST")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Token validity
        if not self.test_token_validity():
            print("\n❌ Token is invalid. Stopping tests.")
            return self.generate_report()
        
        # Test 2: Permissions
        self.test_permissions()
        
        # Test 3: Get pages
        pages = self.get_pages()
        
        # Test 4: Get Instagram accounts
        self.get_instagram_accounts()
        
        # Test 5: Test posting capabilities
        if pages:
            for page in pages:
                self.test_facebook_post(page)
        
        if self.results["instagram_accounts"]:
            for ig in self.results["instagram_accounts"]:
                self.test_instagram_post_capability(ig)
        
        # Generate final report
        return self.generate_report()


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        # Use the token from the request
        token = "EAAOfcn4RZAs4BP4EgZCdf9yismCoPZAGz9gqRvDxZCMLnxJqZAIOQwlXeUzVIAI6AKZAb3pLDEkq8avbMdmucZCCJtPMWCA4ZCAMtUe39lPcp9XWcZAP1fdFjzcI65b3tKqVXd2sj3bqLL7TNAx0zpk5YhuC7cxxmLMJHcJa0gluRP59cluw3ypWxHVT5s3WFCRgXd22fjh9t9oiTwZCsdkmBlt5qUUXR86PrZB0B8szicsxa5aDuHcEnr2zAlw5iJObePZCcrewZBMwChxFHpX7X9oqzLZAaJZCUDS9otAlDmr2UgMBYq7bkAfWPm3IJCchovOB7RYuzpgYl63kr76"
    
    tester = FacebookTokenTester(token)
    results = tester.run_full_test()
    
    # Save results to JSON file
    output_file = "build/facebook_token_test_results.json"
    try:
        import os
        os.makedirs("build", exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")
    
    # Return exit code based on success
    if results["token_valid"] and (results["pages"] or results["instagram_accounts"]):
        print("\n✅ TEST PASSED: Token has access to Facebook/Instagram")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED: Token has limited or no access")
        sys.exit(1)


if __name__ == "__main__":
    main()
