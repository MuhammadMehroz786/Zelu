"""Content service — chunked writing and content management."""

import structlog

logger = structlog.get_logger(__name__)


def chunk_content_for_writing(blueprint: dict) -> list:
    """Break a product blueprint into writing tasks."""
    tasks = []

    main_product = blueprint.get("main_product", {})
    chapters = main_product.get("chapter_outline", [])

    for i, chapter in enumerate(chapters):
        tasks.append({
            "type": "chapter",
            "product_type": "main",
            "index": i,
            "title": chapter if isinstance(chapter, str) else chapter.get("title", f"Chapter {i+1}"),
            "outline": "" if isinstance(chapter, str) else chapter.get("key_points", ""),
        })

    for bonus_key in ["bonus_1", "bonus_2"]:
        bonus = blueprint.get(bonus_key, {})
        if bonus:
            tasks.append({
                "type": "bonus",
                "product_type": bonus_key,
                "title": bonus.get("title", ""),
                "outline": bonus.get("content_outline", ""),
            })

    order_bump = blueprint.get("order_bump", {})
    if order_bump:
        tasks.append({
            "type": "order_bump",
            "product_type": "order_bump",
            "title": order_bump.get("title", ""),
            "outline": order_bump.get("content_outline", ""),
        })

    return tasks


def assemble_product(chapters: list, metadata: dict) -> dict:
    """Assemble written chapters into a complete product."""
    return {
        "title": metadata.get("title", ""),
        "subtitle": metadata.get("subtitle", ""),
        "chapters": chapters,
        "total_words": sum(
            len(ch.get("content", "").split()) for ch in chapters
        ),
        "total_chapters": len(chapters),
    }
