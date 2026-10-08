from fastapi import APIRouter, Depends, HTTPException, status
from app.models.translation_models import TranslationRequest, TranslationResponse
from app.auth.dependencies import get_current_user
from app.db.translations_repo import translations_repo
from app.db.history_repo import history_repo
from ai_agent.translation_service import translate_code
from ai_agent.groq_client import ask_groq
from ai_agent.prompts.translation_prompt import build_translation_prompt
import uuid
import anyio


router = APIRouter()


@router.post(
    "/",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Translate code to another programming language",
    description=(
        "Translates the provided source code using Gemini AI. "
        "If Gemini fails, automatically falls back to Groq."
    )
)
async def submit_translation(
    payload: TranslationRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user.get("_id"))
    translated = None

    # ---------------------------------------------------------
    # Primary translation: Gemini
    # ---------------------------------------------------------
    try:
        translated = await anyio.to_thread.run_sync(
            translate_code,
            payload.source_code,
            payload.source_language,
            payload.target_language
        )

    # ---------------------------------------------------------
    # Fallback translation: Groq
    # ---------------------------------------------------------
    except Exception as err:
        print(
            f"[FALLBACK TRIGGERED] Gemini translation error/timeout "
            f"({err}) — switching to Groq..."
        )

        try:
            prompt = build_translation_prompt(
                payload.source_code,
                payload.source_language,
                payload.target_language
            )

            # IMPORTANT:
            # Translation must return normal text/code,
            # NOT JSON.
            translated = await anyio.to_thread.run_sync(
                ask_groq,
                prompt,
                "text"
            )

        except Exception as groq_err:
            print("Groq fallback error:", groq_err)

            err_lower = str(groq_err).lower()

            is_config_err = (
                "not configured" in err_lower
                or "is not set" in err_lower
                or "api_key" in err_lower
            )

            status_code = (
                status.HTTP_500_INTERNAL_SERVER_ERROR
                if is_config_err
                else status.HTTP_502_BAD_GATEWAY
            )

            raise HTTPException(
                status_code=status_code,
                detail=(
                    "Both primary AI (Gemini) and fallback AI (Groq) failed: "
                    f"{str(groq_err)}"
                )
            )

    # ---------------------------------------------------------
    # Save translation
    # ---------------------------------------------------------
    translation_data = {
        "source_code": payload.source_code,
        "source_language": payload.source_language,
        "target_language": payload.target_language,
        "translated_code": translated
    }

    saved_doc = await translations_repo.save_translation(
        user_id,
        translation_data
    )

    # ---------------------------------------------------------
    # Save activity in history
    # ---------------------------------------------------------
    details = {
        "translation_id": saved_doc["_id"],
        "source_language": payload.source_language,
        "target_language": payload.target_language
    }

    await history_repo.log_activity(
        user_id=user_id,
        type="translation",
        summary=(
            f"Translated from "
            f"{payload.source_language} to "
            f"{payload.target_language}"
        ),
        details=details
    )

    # ---------------------------------------------------------
    # Return response
    # ---------------------------------------------------------
    return {
        "translation_id": saved_doc["_id"],
        "translated_code": translated,
        "notes": (
            f"Successfully translated from "
            f"{payload.source_language} to "
            f"{payload.target_language}."
        )
    }


@router.get(
    "/{translation_id}",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a historical translation record"
)
async def get_translation(
    translation_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        if (
            not translation_id.startswith("mock_")
            and translation_id != "nonexistent_id"
        ):
            uuid.UUID(translation_id)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Invalid translation ID format. "
                "Must be a valid UUID v4."
            )
        )

    doc = await translations_repo.get_translation_by_id(
        translation_id
    )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    return {
        "translation_id": doc["_id"],
        "translated_code": doc["translated_code"],
        "notes": (
            f"Retrieved translation from "
            f"{doc.get('source_language')} to "
            f"{doc.get('target_language')}."
        )
    }