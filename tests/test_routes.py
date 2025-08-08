from app import create_app

app = create_app()

print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
    
print("\nBlueprints:")
for name, blueprint in app.blueprints.items():
    print(f"{name}: {blueprint}")
