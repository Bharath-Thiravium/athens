#!/usr/bin/env python3
"""
Test script to verify that multiple contractors are now being returned
by the all-adminusers endpoint.

Run this script to test the fix for contractor admin listing.
"""

import requests
import json

def test_contractor_listing():
    """Test the contractor listing endpoints"""
    
    # Base URL - adjust as needed
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Contractor Admin Listing Fix")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        "/authentication/all-adminusers/",
        "/authentication/debug-contractors/",
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing endpoint: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                
                if endpoint == "/authentication/all-adminusers/":
                    print(f"✅ Status: {response.status_code}")
                    print(f"📊 Total users: {data.get('total_count', 0)}")
                    
                    summary = data.get('summary', {})
                    print(f"📋 Summary:")
                    print(f"   - Client users: {summary.get('clientuser_count', 0)}")
                    print(f"   - EPC users: {summary.get('epcuser_count', 0)}")
                    print(f"   - Contractor users: {summary.get('contractoruser_count', 0)}")
                    print(f"   - Client admins: {summary.get('client_admin_count', 0)}")
                    print(f"   - EPC admins: {summary.get('epc_admin_count', 0)}")
                    print(f"   - Contractor admins: {summary.get('contractor_admin_count', 0)}")
                    print(f"   - Total contractors: {summary.get('total_contractor_count', 0)}")
                    
                    # Check for contractor admins specifically
                    users = data.get('users', [])
                    contractor_admins = [u for u in users if u.get('admin_type') == 'contractor']
                    
                    print(f"\n🏗️ Contractor Admins Found: {len(contractor_admins)}")
                    for i, contractor in enumerate(contractor_admins[:5]):  # Show first 5
                        print(f"   {i+1}. {contractor.get('username')} - {contractor.get('company_name')} (Project: {contractor.get('project')})")
                    
                    if len(contractor_admins) > 5:
                        print(f"   ... and {len(contractor_admins) - 5} more")
                
                elif endpoint == "/authentication/debug-contractors/":
                    print(f"✅ Status: {response.status_code}")
                    print(f"📊 Total contractor admins: {data.get('total_contractor_admins', 0)}")
                    
                    projects = data.get('projects', {})
                    print(f"📋 Projects with contractors: {len(projects)}")
                    
                    for project_id, project_data in projects.items():
                        contractors = project_data.get('contractors', [])
                        print(f"   - {project_data.get('project_name', 'Unknown')} (ID: {project_id}): {len(contractors)} contractors")
                        for contractor in contractors:
                            print(f"     * {contractor.get('username')} - {contractor.get('company_name')}")
                    
                    summary = data.get('summary', {})
                    print(f"\n📈 Summary:")
                    print(f"   - Projects with contractors: {summary.get('projects_with_contractors', 0)}")
                    print(f"   - Projects with multiple contractors: {summary.get('projects_with_multiple_contractors', 0)}")
            
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - make sure Django server is running on {base_url}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    print("\n💡 Expected results after fix:")
    print("   - all-adminusers should include contractor admins (admin_type='contractor')")
    print("   - debug-contractors should show projects with multiple contractors")
    print("   - MomLive should now show all contractor admins in participant selection")

if __name__ == "__main__":
    test_contractor_listing()
