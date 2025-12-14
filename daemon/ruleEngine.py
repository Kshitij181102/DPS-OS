# daemon/ruleEngine.py
import json, time

class RuleEngine:
    def __init__(self, dbPath):
        # For prototype, load rules from schema/ruleSchema.json
        with open('schema/ruleSchema.json') as f:
            self.rules = json.load(f)
        self.lastTriggerTimes = {}

    def evaluate(self, event):
        # event: {"trigger":"usbPlugged","device":{...}}
        candidates = []
        for edge in self.rules.get('edges',[]):
            if edge['trigger'] != event.get('trigger'):
                continue
            cond = edge.get('conditions',{})
            if 'urlPattern' in cond and 'url' in event:
                url = event['url']
                if not any(pat.replace('*','') in url for pat in cond['urlPattern']):
                    continue
            candidates.append(edge)
        if not candidates: return None
        candidates.sort(key=lambda e: e.get('priority',0), reverse=True)
        selected = candidates[0]
        # cooldown check
        key = selected.get('trigger') + json.dumps(selected.get('conditions',{}))
        now = time.time()
        if selected.get('cooldownSeconds'):
            last = self.lastTriggerTimes.get(key,0)
            if now - last < selected['cooldownSeconds']:
                return None
            self.lastTriggerTimes[key] = now
        return selected