# Backend Optimization Module
# Add these optimizations to myapp/api_utils.py (create new file)

from django.core.paginator import Paginator
from django.conf import settings
from functools import wraps
import logging
from django.views.decorators.cache import cache_page
from django.core.cache import cache

logger = logging.getLogger(__name__)

# ==================== PAGINATION UTILITY ====================
class OptimizedPaginator:
    """Implement pagination for large responses to avoid bulk data transfer"""
    
    DEFAULT_PAGE_SIZE = 25
    MAX_PAGE_SIZE = 100
    
    @staticmethod
    def paginate_queryset(queryset, page=1, page_size=None):
        """
        Paginate a queryset to optimize data transfer
        
        Args:
            queryset: Django ORM queryset
            page: Page number (default 1)
            page_size: Items per page (default 25, max 100)
        
        Returns:
            dict with paginated data and metadata
        """
        if page_size is None:
            page_size = OptimizedPaginator.DEFAULT_PAGE_SIZE
        
        # Enforce maximum page size
        page_size = min(page_size, OptimizedPaginator.MAX_PAGE_SIZE)
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        return {
            'items': list(page_obj.object_list),
            'total_count': paginator.count,
            'page': page_obj.number,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }

# ==================== ASYNC TASK UTILITIES ====================
import asyncio
from asgiref.sync import async_to_sync

@async_to_sync
async def async_bulk_update(model, objects):
    """
    Perform bulk updates asynchronously
    
    Example:
        async_bulk_update(Project, projects_to_update)
    """
    await asyncio.to_thread(lambda: model.objects.bulk_update(objects, batch_size=1000))
    logger.info(f"Bulk updated {len(objects)} {model.__name__} objects")

# ==================== QUERY OPTIMIZATION ====================
def select_related_prefetch(*relations):
    """
    Decorator for optimizing database queries using select_related/prefetch_related
    
    Example:
        @select_related_prefetch('project', 'assigned_to')
        def get_tasks():
            return Task.objects.all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            queryset = func(*args, **kwargs)
            
            # Use select_related for ForeignKey and OneToOne
            # Use prefetch_related for ManyToMany and reverse ForeignKey
            for relation in relations:
                if '__' in relation:
                    # Nested relationships
                    queryset = queryset.prefetch_related(relation)
                else:
                    queryset = queryset.select_related(relation)
            
            return queryset
        return wrapper
    return decorator

# ==================== CACHING OPTIMIZATIONS ====================
def cache_based_on_user(timeout=300):
    """
    Cache view responses per user to avoid redundant processing
    
    Example:
        @cache_based_on_user(timeout=600)
        def user_dashboard(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return func(request, *args, **kwargs)
            
            cache_key = f"view_{func.__name__}_{request.user.id}"
            result = cache.get(cache_key)
            
            if result is None:
                result = func(request, *args, **kwargs)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

# ==================== BATCH PROCESSING ====================
def batch_process(items, batch_size=1000, process_func=None):
    """
    Process large lists in batches to avoid memory issues
    
    Example:
        for batch in batch_process(large_list, batch_size=500):
            process_batch(batch)
    """
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        if process_func:
            process_func(batch)
        else:
            yield batch

# ==================== LAZY EVALUATION ====================
def lazy_import(module_path):
    """
    Lazily import modules only when needed to reduce startup time
    
    Example:
        pd = lazy_import('pandas')
    """
    import importlib
    def _lazy_import(*args, **kwargs):
        module = importlib.import_module(module_path)
        return module
    return _lazy_import

# ==================== QUERY RESULT LIMITING ====================
class OptimizedQuerySet:
    """Helper class for optimized query operations"""
    
    @staticmethod
    def get_with_limit(model, limit=1000, **filters):
        """
        Get queryset with automatic limit to prevent memory issues
        
        Usage:
            users = OptimizedQuerySet.get_with_limit(User, limit=500, status='active')
        """
        return model.objects.filter(**filters)[:limit]
    
    @staticmethod
    def get_values_list_optimized(model, fields, limit=1000, **filters):
        """
        Get specific fields only (reduces memory footprint)
        
        Usage:
            user_emails = OptimizedQuerySet.get_values_list_optimized(
                User, 
                fields=['id', 'email'],
                limit=500
            )
        """
        return model.objects.filter(**filters).values_list(*fields)[:limit]

# ==================== LOGGING OPTIMIZATION ====================
class OptimizedLogger:
    """Minimal logging for production"""
    
    @staticmethod
    def log_only_errors(func):
        """
        Only log errors, not info/debug in production
        
        Example:
            @OptimizedLogger.log_only_errors
            def risky_operation():
                ...
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
