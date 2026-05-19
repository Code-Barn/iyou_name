"""
DID-related views for Namecharts (aka iyou_name).

Provides API endpoints for DID generation, VC issuance, and verification.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from apps.users.did_utils import generate_did as utils_generate_did
from apps.users.did_utils import generate_key as utils_generate_key
from apps.users.did_utils import issue_vc as utils_issue_vc
from apps.users.did_utils import verify_vc as utils_verify_vc

logger = logging.getLogger(__name__)


@login_required
@csrf_protect
@require_http_methods(["POST"])
def generate_did(request):
    """
    Generate a new DID for the authenticated user.

    POST /api/did/generate/

    Request body (optional):
        {"method": "key"}

    Response:
        {"did": "did:key:..."}
    """
    try:
        data = json.loads(request.body) if request.body else {}
        method = data.get("method", "key")

        user = request.user

        if user.did:
            return JsonResponse(
                {
                    "did": user.did,
                    "message": "User already has a DID",
                    "generated": False,
                }
            )

        did = utils_generate_did(method)

        user.did = did
        user.did_method = method
        user.save(update_fields=["did", "did_method"])

        logger.info(f"Generated DID for user {user.username}: {did}")

        return JsonResponse({"did": did, "method": method, "generated": True})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error generating DID: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_did(request):
    """
    Get the current user's DID if it exists.

    GET /api/did/

    Response:
        {"did": "did:key:...", "has_did": true}
    """
    user = request.user
    return JsonResponse(
        {
            "did": user.did,
            "has_did": bool(user.did),
            "method": user.did_method if user.did else None,
        }
    )


@login_required
@csrf_protect
@require_http_methods(["POST"])
def verify_vc(request):
    """
    Verify a verifiable credential.

    POST /api/did/verify/

    Request body:
        {"vc": "{\"@context\": ..., \"credentialSubject\": ...}"}

    Response:
        {"valid": true/false}
    """
    try:
        data = json.loads(request.body) if request.body else {}
        vc = data.get("vc")

        if not vc:
            return JsonResponse({"error": "VC is required"}, status=400)

        is_valid = utils_verify_vc(vc)

        return JsonResponse({"valid": is_valid})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error verifying VC: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_protect
@require_http_methods(["POST"])
def issue_vc(request):
    """
    Issue a verifiable credential for the authenticated user.

    POST /api/did/vc/issue/

    Request body:
        {
            "credentialSubject": {"id": "did:key:...", "name": "John Doe"},
            "type": ["VerifiableCredential", "NameCredential"],
            "name": "optional name for storage"
        }

    Response:
        {"success": true, "vc": {...}, "vc_count": 3}
    """
    try:
        data = json.loads(request.body) if request.body else {}
        credential_subject = data.get("credentialSubject", {})
        vc_type = data.get("type", ["VerifiableCredential", "GenericCredential"])
        name = data.get("name")

        user = request.user

        if not user.did:
            return JsonResponse(
                {"error": "User does not have a DID. Call /api/did/generate/ first."},
                status=400,
            )

        if not user.did_key:
            return JsonResponse(
                {"error": "User does not have a key. Generate one first."}, status=400
            )

        import datetime

        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            "type": vc_type,
            "issuer": user.did,
            "issuanceDate": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "credentialSubject": credential_subject,
        }

        vc_json = utils_issue_vc(credential, user.did, user.did_key)

        if not vc_json:
            return JsonResponse({"error": "Failed to issue VC"}, status=500)

        vc = json.loads(vc_json)
        user.add_vc(vc, name)
        user.save(update_fields=["vcs"])

        logger.info(f"Issued VC for user {user.username}")

        return JsonResponse({"success": True, "vc": vc, "vc_count": len(user.vcs)})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error issuing VC: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_vc(request):
    """
    Add a verifiable credential to the user's profile.

    POST /api/did/vc/add/

    Request body:
        {"vc": {...}, "name": "optional name"}

    Response:
        {"success": true, "vc_count": 3}
    """
    try:
        data = json.loads(request.body) if request.body else {}
        vc = data.get("vc")
        name = data.get("name")

        if not vc:
            return JsonResponse({"error": "VC is required"}, status=400)

        if not isinstance(vc, dict):
            return JsonResponse({"error": "VC must be a JSON object"}, status=400)

        user = request.user
        user.add_vc(vc, name)
        user.save(update_fields=["vcs"])

        logger.info(f"Added VC to user {user.username}")

        return JsonResponse({"success": True, "vc_count": len(user.vcs)})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error adding VC: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def list_vcs(request):
    """
    List all VCs associated with the current user.

    GET /api/did/vcs/

    Response:
        {"vcs": [{"credential": {...}, "name": "...", ...}, ...]}
    """
    user = request.user
    return JsonResponse({"vcs": user.vcs or [], "count": len(user.vcs or [])})


@login_required
@require_http_methods(["GET"])
def get_vcs_by_type(request, vc_type):
    """
    Get all VCs of a specific type.

    GET /api/did/vcs/type/<vc_type>/

    Response:
        {"vcs": [...], "count": 2}
    """
    user = request.user
    vcs = user.get_vcs_by_type(vc_type)
    return JsonResponse({"vcs": vcs, "count": len(vcs)})
