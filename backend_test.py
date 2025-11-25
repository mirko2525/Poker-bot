#!/usr/bin/env python3
"""
Backend API Testing Suite for Table Screenshot Recognition API
Tests the new /api/table/1/cards endpoint and existing demo endpoints.
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import Dict, Any

# Get backend URL from frontend .env
BACKEND_URL = "https://poker-assistant-2.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.screenshot_path = Path("/app/backend/data/screens/table1.png")
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_table_cards_with_screenshot(self):
        """Test /api/table/1/cards endpoint when screenshot exists"""
        try:
            # Ensure screenshot exists
            if not self.screenshot_path.exists():
                self.log_test("Table Cards API - With Screenshot", False, 
                            f"Screenshot not found at {self.screenshot_path}")
                return
            
            response = requests.get(f"{self.backend_url}/table/1/cards", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Table Cards API - With Screenshot", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return
            
            # Check JSON response structure
            data = response.json()
            required_fields = ["table_id", "image_path", "status", "hero", "board"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Table Cards API - With Screenshot", False, 
                            f"Missing required fields: {missing_fields}")
                return
            
            # Verify table_id
            if data["table_id"] != "1":
                self.log_test("Table Cards API - With Screenshot", False, 
                            f"Expected table_id '1', got '{data['table_id']}'")
                return
            
            # Verify status is ok, pending, or error (not no_image since file exists)
            if data["status"] not in ["ok", "pending", "error"]:
                self.log_test("Table Cards API - With Screenshot", False, 
                            f"Unexpected status '{data['status']}' when screenshot exists")
                return
            
            # Verify hero and board are lists
            if not isinstance(data["hero"], list) or not isinstance(data["board"], list):
                self.log_test("Table Cards API - With Screenshot", False, 
                            "Hero and board should be lists")
                return
            
            # Check RecognizedCard structure if cards are present
            for card_list_name, card_list in [("hero", data["hero"]), ("board", data["board"])]:
                for i, card in enumerate(card_list):
                    required_card_fields = ["code", "score", "conf"]
                    missing_card_fields = [field for field in required_card_fields if field not in card]
                    if missing_card_fields:
                        self.log_test("Table Cards API - With Screenshot", False, 
                                    f"Missing fields in {card_list_name}[{i}]: {missing_card_fields}")
                        return
            
            self.log_test("Table Cards API - With Screenshot", True, 
                        f"Status: {data['status']}, Hero cards: {len(data['hero'])}, Board cards: {len(data['board'])}")
            
        except requests.exceptions.RequestException as e:
            self.log_test("Table Cards API - With Screenshot", False, f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            self.log_test("Table Cards API - With Screenshot", False, f"Invalid JSON response: {str(e)}")
        except Exception as e:
            self.log_test("Table Cards API - With Screenshot", False, f"Unexpected error: {str(e)}")

    def test_table_cards_without_screenshot(self):
        """Test /api/table/1/cards endpoint when screenshot is missing"""
        try:
            # Temporarily move screenshot if it exists
            backup_path = None
            if self.screenshot_path.exists():
                backup_path = self.screenshot_path.with_suffix('.backup')
                self.screenshot_path.rename(backup_path)
            
            # Wait a moment for the background watcher to detect the missing file
            time.sleep(6)  # Watcher runs every 5 seconds
            
            response = requests.get(f"{self.backend_url}/table/1/cards", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Table Cards API - Without Screenshot", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return
            
            data = response.json()
            
            # Should return no_image or error status when file is missing
            if data["status"] not in ["no_image", "error"]:
                self.log_test("Table Cards API - Without Screenshot", False, 
                            f"Expected status 'no_image' or 'error', got '{data['status']}'")
                return
            
            # Should not crash - we got a valid response
            self.log_test("Table Cards API - Without Screenshot", True, 
                        f"Correctly returned status '{data['status']}' when screenshot missing")
            
        except requests.exceptions.RequestException as e:
            self.log_test("Table Cards API - Without Screenshot", False, f"Request failed: {str(e)}")
        except Exception as e:
            self.log_test("Table Cards API - Without Screenshot", False, f"Unexpected error: {str(e)}")
        finally:
            # Restore screenshot if we moved it
            if backup_path and backup_path.exists():
                backup_path.rename(self.screenshot_path)

    def test_invalid_table_id(self):
        """Test /api/table/{invalid_id}/cards endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/table/999/cards", timeout=30)
            
            if response.status_code != 404:
                self.log_test("Table Cards API - Invalid Table ID", False, 
                            f"Expected 404, got {response.status_code}")
                return
            
            self.log_test("Table Cards API - Invalid Table ID", True, 
                        "Correctly returned 404 for invalid table_id")
            
        except requests.exceptions.RequestException as e:
            self.log_test("Table Cards API - Invalid Table ID", False, f"Request failed: {str(e)}")
        except Exception as e:
            self.log_test("Table Cards API - Invalid Table ID", False, f"Unexpected error: {str(e)}")

    def test_demo_start_endpoint(self):
        """Test /api/poker/demo/start endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/poker/demo/start", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Demo Start Endpoint", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return
            
            data = response.json()
            
            if "message" not in data or "total_hands" not in data:
                self.log_test("Demo Start Endpoint", False, 
                            "Missing required fields: message, total_hands")
                return
            
            if data["total_hands"] != 8:  # Based on mock data in server.py
                self.log_test("Demo Start Endpoint", False, 
                            f"Expected 8 total_hands, got {data['total_hands']}")
                return
            
            self.log_test("Demo Start Endpoint", True, 
                        f"Message: {data['message']}, Total hands: {data['total_hands']}")
            
        except requests.exceptions.RequestException as e:
            self.log_test("Demo Start Endpoint", False, f"Request failed: {str(e)}")
        except Exception as e:
            self.log_test("Demo Start Endpoint", False, f"Unexpected error: {str(e)}")

    def test_demo_next_endpoint(self):
        """Test /api/poker/demo/next endpoint"""
        try:
            # First start the demo
            requests.get(f"{self.backend_url}/poker/demo/start", timeout=30)
            
            response = requests.get(f"{self.backend_url}/poker/demo/next", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Demo Next Endpoint", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return
            
            data = response.json()
            
            required_fields = ["hand_number", "hand_state", "decision", "has_next"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Demo Next Endpoint", False, 
                            f"Missing required fields: {missing_fields}")
                return
            
            # Check hand_state structure
            hand_state = data["hand_state"]
            required_hand_fields = ["hero_cards", "board_cards", "hero_stack", "pot_size", "to_call", "big_blind", "players_in_hand", "phase"]
            missing_hand_fields = [field for field in required_hand_fields if field not in hand_state]
            
            if missing_hand_fields:
                self.log_test("Demo Next Endpoint", False, 
                            f"Missing hand_state fields: {missing_hand_fields}")
                return
            
            # Check decision structure
            decision = data["decision"]
            required_decision_fields = ["action", "equity"]
            missing_decision_fields = [field for field in required_decision_fields if field not in decision]
            
            if missing_decision_fields:
                self.log_test("Demo Next Endpoint", False, 
                            f"Missing decision fields: {missing_decision_fields}")
                return
            
            self.log_test("Demo Next Endpoint", True, 
                        f"Hand {data['hand_number']}, Action: {decision['action']}, Equity: {decision['equity']:.1%}")
            
        except requests.exceptions.RequestException as e:
            self.log_test("Demo Next Endpoint", False, f"Request failed: {str(e)}")
        except Exception as e:
            self.log_test("Demo Next Endpoint", False, f"Unexpected error: {str(e)}")

    def test_demo_status_endpoint(self):
        """Test /api/poker/demo/status endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/poker/demo/status", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Demo Status Endpoint", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return
            
            data = response.json()
            
            required_fields = ["current_hand", "total_hands", "has_next"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Demo Status Endpoint", False, 
                            f"Missing required fields: {missing_fields}")
                return
            
            self.log_test("Demo Status Endpoint", True, 
                        f"Current hand: {data['current_hand']}, Total: {data['total_hands']}, Has next: {data['has_next']}")
            
        except requests.exceptions.RequestException as e:
            self.log_test("Demo Status Endpoint", False, f"Request failed: {str(e)}")
        except Exception as e:
            self.log_test("Demo Status Endpoint", False, f"Unexpected error: {str(e)}")

    def test_background_watcher_startup(self):
        """Test that background watcher doesn't block startup"""
        try:
            # Test that we can make requests (indicating server started successfully)
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/", timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_test("Background Watcher Startup", False, 
                            f"Server not responding, status: {response.status_code}")
                return
            
            # If we get a response quickly, the watcher didn't block startup
            if response_time > 10:  # Arbitrary threshold
                self.log_test("Background Watcher Startup", False, 
                            f"Server response too slow ({response_time:.1f}s), may indicate blocking")
                return
            
            self.log_test("Background Watcher Startup", True, 
                        f"Server responding normally ({response_time:.2f}s), watcher not blocking startup")
            
        except requests.exceptions.RequestException as e:
            self.log_test("Background Watcher Startup", False, f"Server not accessible: {str(e)}")
        except Exception as e:
            self.log_test("Background Watcher Startup", False, f"Unexpected error: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("BACKEND API TESTING SUITE")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Screenshot path: {self.screenshot_path}")
        print("=" * 60)
        print()
        
        # Test background watcher startup first
        self.test_background_watcher_startup()
        
        # Test existing demo endpoints
        self.test_demo_start_endpoint()
        self.test_demo_next_endpoint()
        self.test_demo_status_endpoint()
        
        # Test new table cards endpoint
        self.test_table_cards_with_screenshot()
        self.test_table_cards_without_screenshot()
        self.test_invalid_table_id()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["passed"])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        print()
        
        if passed < total:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"❌ {result['test']}: {result['details']}")
            print()
        
        return passed == total

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)