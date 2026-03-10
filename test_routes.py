"""
Test script to verify BMSmart backend routes.
"""
from app import create_app

app = create_app('development')

print('\n=== BMSmart Backend - Registered Routes ===\n')

routes = []
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        routes.append(f'{methods:20} {rule.rule}')

routes.sort()
for route in routes:
    print(route)

print(f'\nTotal routes: {len(routes)}')
print('\n=== Application ready! ===\n')
