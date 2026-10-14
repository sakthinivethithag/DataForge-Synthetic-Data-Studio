from datetime import datetime, timezone
import json
from flask import Response

def passport(metadata, evaluation, privacy):
    payload = {"title":"DataForge Synthetic Data Passport","generated_at":datetime.now(timezone.utc).isoformat(),
      "dataset":metadata,"generation":metadata.get("generation",{}),"utility_evaluation":evaluation,
      "privacy_checks":privacy,"limitations":[
        "This passport summarizes a local academic demonstration.",
        "Statistical similarity does not establish downstream model utility.",
        "Heuristic privacy checks do not prove anonymity or provide differential privacy.",
        "Review sensitive fields and legal obligations before sharing any generated dataset."
      ]}
    return payload

def json_response(payload):
    return Response(json.dumps(payload, indent=2, default=str), mimetype="application/json",
                    headers={"Content-Disposition":"attachment; filename=dataforge_passport.json"})
