from modules.premium_studio import FluxGenerator
import os

print("Initializing FluxGenerator...")
generator = FluxGenerator()

# Force check the fallback method directly to see if it generates the concept card
print("Testing local fallback generation...")
prompt = "A futuristic city with flying cars"
output = generator._generate_local_fallback(prompt, 1024, 1024)

print(f"Generated output: {output}")

if output and os.path.exists(output[0]):
    print(f"SUCCESS: Fallback image generated at {output[0]}")
else:
    print("FAILURE: Fallback image generation failed.")
