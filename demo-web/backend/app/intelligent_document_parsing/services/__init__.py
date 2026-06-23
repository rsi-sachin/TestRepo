"""High-level service modules."""

from .document_analysis_service import DocumentAnalysisService
from .user_feedback_handler import UserFeedbackHandler, UserFeedback, FeedbackStats
from .information_index_manager import InformationIndexManager
from .reference_document_resolver import ReferenceDocumentResolver, create_reference_resolver
from .information_index_integrator import (
    create_global_fact_from_decision,
    create_global_facts_from_analysis,
    extract_referenced_documents,
    create_document_specific_facts,
    populate_global_index_from_section_4_1,
    create_postponed_action_item_for_reference_retrieval,
)

__all__ = [
    'DocumentAnalysisService',
    'UserFeedbackHandler',
    'UserFeedback',
    'FeedbackStats',
    'InformationIndexManager',
    'ReferenceDocumentResolver',
    'create_reference_resolver',
    # Integration functions
    'create_global_fact_from_decision',
    'create_global_facts_from_analysis',
    'extract_referenced_documents',
    'create_document_specific_facts',
    'populate_global_index_from_section_4_1',
    'create_postponed_action_item_for_reference_retrieval',
]
