import os
from google import genai # Use the new unified SDK
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models import SessionLocal, Product, engine, Base

load_dotenv()

# Initialize the modern Client
# It will automatically find your AI_API_KEY from the .env
client = genai.Client(api_key=os.getenv("AI_API_KEY")) 

def get_embedding(text: str):
    """Generates a 3072-dimension vector using the new gemini-embedding-001."""
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return response.embeddings[0].values


PRODUCT_DATA = [
    # Electronics & Tech
    {"name": "UltraWide Monitor", "desc": "34-inch curved screen for immersive gaming and productivity."},
    {"name": "Mechanical Keyboard", "desc": "Tactile blue switches with RGB backlighting for developers."},
    {"name": "Noise Cancelling Headphones", "desc": "Over-ear wireless headphones with active noise cancellation for deep focus."},
    {"name": "Smartphone Gimbal", "desc": "3-axis stabilizer for smooth cinematic video recording on mobile."},
    {"name": "Portable SSD 2TB", "desc": "High-speed external storage for backing up large video files and projects."},
    {"name": "Webcam 4K", "desc": "Ultra HD camera with dual microphones for professional video conferencing."},
    {"name": "Smart Home Hub", "desc": "Central controller for your smart lights, locks, and thermostats."},
    {"name": "Wireless Mouse", "desc": "Ergonomic vertical mouse designed to reduce wrist strain during long hours."},
    {"name": "Gaming Laptop", "desc": "RTX 4080 powered laptop for high-performance creative work and gaming."},
    {"name": "Tablet Pro", "desc": "12.9-inch display with stylus support for digital artists and designers."},
    
    # Fashion & Apparel
    {"name": "Waterproof Parka", "desc": "Heavy-duty winter coat designed for sub-zero temperatures and snow."},
    {"name": "Running Shoes", "desc": "Lightweight breathable sneakers for marathon training and daily jogs."},
    {"name": "Leather Chelsea Boots", "desc": "Classic slip-on boots made from premium Italian leather."},
    {"name": "Denim Jacket", "desc": "Timeless blue jean jacket with a relaxed fit for casual outings."},
    {"name": "Yoga Leggings", "desc": "High-waisted moisture-wicking pants for gym workouts and yoga sessions."},
    {"name": "Linen Summer Shirt", "desc": "Breathable white shirt perfect for hot beach weather."},
    {"name": "Silk Necktie", "desc": "Elegant navy tie for formal business meetings and weddings."},
    {"name": "Polarized Sunglasses", "desc": "UV protection eyewear with anti-glare lenses for driving and hiking."},
    {"name": "Canvas Backpack", "desc": "Durable vintage-style rucksack for school, work, or weekend trips."},
    {"name": "Wool Beanie", "desc": "Soft ribbed knit hat to keep you warm during autumn and winter."},

    # Home & Kitchen
    {"name": "Air Fryer", "desc": "Fast circulation oven for healthy cooking with minimal oil."},
    {"name": "Espresso Machine", "desc": "Professional grade coffee maker with milk frothing wand."},
    {"name": "Cast Iron Skillet", "desc": "Heavy-duty pan for perfect searing and oven-to-table cooking."},
    {"name": "Robot Vacuum", "desc": "Self-charging smart vacuum that maps your house for daily cleaning."},
    {"name": "Standing Desk", "desc": "Electric height-adjustable desk for a healthier work-from-home setup."},
    {"name": "Memory Foam Pillow", "desc": "Contoured support for neck pain relief and better sleep quality."},
    {"name": "Non-Stick Cookware Set", "desc": "10-piece ceramic coated pans for easy cleanup and healthy meals."},
    {"name": "Aromatherapy Diffuser", "desc": "Ultrasonic cool mist humidifier with color-changing LED lights."},
    {"name": "Chef's Knife", "desc": "8-inch forged high-carbon steel blade for precision slicing."},
    {"name": "Electric Kettle", "desc": "Stainless steel rapid-boil kettle with automatic shut-off."},

    # Fitness & Outdoors
    {"name": "Adjustable Dumbbells", "desc": "Space-saving weight set for home strength training and bulking."},
    {"name": "Camping Tent", "desc": "4-person waterproof tent with easy setup for outdoor adventures."},
    {"name": "Yoga Mat", "desc": "Non-slip eco-friendly mat with extra cushioning for joints."},
    {"name": "Mountain Bike", "desc": "21-speed trail bike with front suspension and disc brakes."},
    {"name": "Hydration Bladder", "desc": "2-liter leak-proof water reservoir for hiking backpacks."},
    {"name": "Resistance Bands", "desc": "Set of 5 elastic bands for physical therapy and muscle toning."},
    {"name": "Electric Scooter", "desc": "Foldable commuter scooter with 20-mile range and LED display."},
    {"name": "Portable Grill", "desc": "Compact charcoal BBQ for tailgating, picnics, and camping."},
    {"name": "Hammock", "desc": "Double nylon swing for relaxing in the backyard or forest."},
    {"name": "Fitness Tracker", "desc": "Waterproof smartwatch that monitors heart rate, sleep, and steps."},

    # Hobbies & Miscellaneous
    {"name": "Acoustic Guitar", "desc": "Full-size steel string guitar with a rich warm tone for beginners."},
    {"name": "Instant Camera", "desc": "Analog film camera that prints photos instantly for nostalgic memories."},
    {"name": "Board Game Set", "desc": "Strategy-based tabletop game for 2-4 players, great for family nights."},
    {"name": "Oil Paint Kit", "desc": "Complete art set including 24 colors, brushes, and canvases."},
    {"name": "Drones with Camera", "desc": "Foldable quadcopter with GPS and 4K video for aerial photography."},
    {"name": "Gardening Tool Set", "desc": "Ergonomic shovels, rakes, and shears for backyard flower beds."},
    {"name": "Mechanical Tool Kit", "desc": "150-piece socket and wrench set for car repairs and DIY projects."},
    {"name": "Telescope", "desc": "Reflector telescope for stargazing and observing craters on the moon."},
    {"name": "Bluetooth Speaker", "desc": "Rugged waterproof speaker with 24-hour battery life and deep bass."},
    {"name": "E-Reader", "desc": "Paper-like display with adjustable warmth for reading thousands of books."}
]

def seed():
    # 1. Manually enable the extension first
    with engine.connect() as conn:
        print("Enabling pgvector extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # 2. Now create the tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    print(f"Starting seed of {len(PRODUCT_DATA)} items...")
    
    for i, item in enumerate(PRODUCT_DATA):
        try:
            # Generate embedding using the new client logic
            vector = get_embedding(item['desc'])
            
            product = Product(
                name=item['name'], 
                description=item['desc'], 
                embedding=vector
            )
            db.add(product)
            
            if (i + 1) % 10 == 0:
                print(f"Progress: {i + 1}/{len(PRODUCT_DATA)}...")
                db.commit() 
        except Exception as e:
            print(f"Error seeding item {i}: {e}")
            db.rollback()

    db.commit()
    print("Success! Database is now seeded with high-quality 3072-dim vectors.")

if __name__ == "__main__":
    seed()