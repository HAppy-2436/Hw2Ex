from .subjects import bp as subjects_bp
from .books import bp as books_bp
from .knowledge_nodes import bp as knowledge_nodes_bp
from .homework import bp as homework_bp
from .learning import bp as learning_bp
from .ai import bp as ai_bp
from .learning_records import bp as learning_records_bp
from .conversations import bp as conversations_bp
from .messages import bp as messages_bp
from .user_profiles import bp as user_profiles_bp
from .conversation_contexts import bp as conversation_contexts_bp
from .review_plans import bp as review_plans_bp
from .review_checkpoints import bp as review_checkpoints_bp
from .review import bp as review_bp
from .reports import bp as reports_bp
from .analytics import bp as analytics_bp

__all__ = [
    'subjects_bp', 'books_bp', 'knowledge_nodes_bp', 'homework_bp',
    'learning_bp', 'ai_bp', 'learning_records_bp', 'conversations_bp', 'messages_bp',
    'user_profiles_bp', 'conversation_contexts_bp', 'review_plans_bp', 'review_checkpoints_bp',
    'review_bp', 'reports_bp', 'analytics_bp'
]