
import asyncio
import os
from pathlib import Path
from poker_vision_ai import PokerVisionAI

async def test_vision():
    print("🚀 TEST VISION AI (Gemini)")
    
    # Check image
    img_path = Path("/app/backend/data/screens/table1.png")
    if not img_path.exists():
        print(f"❌ Image not found at {img_path}")
        # Create a dummy image if needed or just fail
        return

    print(f"📸 Using image: {img_path}")
    
    try:
        vision_ai = PokerVisionAI()
        print("✅ PokerVisionAI initialized")
        
        print("🧠 Analyzing...")
        result = await vision_ai.analyze_poker_table(str(img_path), table_id=1)
        
        print("\n📊 RESULT:")
        print(f"   Hero: {result.get('hero_cards')}")
        print(f"   Board: {result.get('board_cards')}")
        print(f"   Action: {result.get('recommended_action')}")
        print(f"   Comment: {result.get('ai_comment')[:100]}...")
        
        print("\n✅ Test Passed!")
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_vision())
