# Enhanced Project Search Implementation Guide

## Overview
This guide provides a comprehensive plan to enhance your AI chatbot's project search capabilities using RAG (Retrieval-Augmented Generation) with PostgreSQL.

## Current Issues Identified

1. **Limited Project Data Indexing** - Only basic fields indexed
2. **Insufficient Keywords** - Only 'project' and 'site' trigger searches  
3. **No Project-Specific Logic** - Generic search doesn't handle relationships
4. **Missing Related Data** - No connection to safety observations, incidents, permits

## Enhanced Solution Architecture

### 1. Enhanced Project RAG Service (`enhanced_project_rag_service.py`)
- **Comprehensive Data Collection**: Indexes all project fields including dates, contacts, locations
- **Related Data Integration**: Includes safety observations, incidents, permits, workers, manpower
- **Smart Chunking**: Creates multiple embeddings per project for different aspects
- **Contextual Summaries**: Generates relevant summaries based on query context

### 2. Enhanced Hybrid RAG Service (`enhanced_hybrid_rag_service.py`)
- **Intelligent Query Routing**: Detects project-focused queries automatically
- **Enhanced Keywords**: 40+ project-related keywords vs. current 2
- **Weighted Scoring**: Boosts project results when relevant
- **Fallback Mechanisms**: Graceful degradation to existing services

### 3. Enhanced Views (`enhanced_views.py`)
- **Multiple Search Types**: Auto, project-specific, general search modes
- **Comprehensive Results**: Returns full project context with related data
- **Statistics Endpoint**: Project overview and metrics
- **Enhanced Index Management**: Rebuilds with comprehensive project data

## Implementation Steps

### Step 1: Update Your Current Views
Replace your existing RAG query view in `backend/ai_bot/views.py`:

```python
# Add this import at the top
from .enhanced_hybrid_rag_service import EnhancedHybridRAGService

# Replace the existing RAGQueryView.post method
class RAGQueryView(APIView):
    def post(self, request):
        self._validate_user_access(request.user)
        question = sanitize_log_input(request.data.get('query', ''))
        if not question:
            return Response({'success': False, 'error': 'query is required'}, status=400)
        
        try:
            # Use enhanced hybrid service
            rag = EnhancedHybridRAGService()
            result = rag.query(question)
        except Exception:
            # Fallback chain as before
            try:
                result = VectorRAGService().query(question)
            except Exception:
                result = RAGService().answer(question)
        
        return Response({'success': True, 'data': result})
```

### Step 2: Add Enhanced URLs
Add to your `backend/ai_bot/urls.py`:

```python
from .enhanced_urls import enhanced_urlpatterns

urlpatterns = [
    # Your existing patterns
    # ...
] + enhanced_urlpatterns
```

### Step 3: Update Vector RAG Service
Modify `backend/ai_bot/vector_rag_service.py` line 121-122:

```python
# Replace the existing project collection code
if Project:
    for pr in Project.objects.all().only(
        'id','projectName','projectCategory','location','capacity',
        'nearestPoliceStation','nearestHospital','commencementDate','deadlineDate'
    )[:5000]:
        # Create comprehensive project text with all relevant fields
        project_text = f"Project {getattr(pr,'projectName','')} Category {getattr(pr,'projectCategory','')} Location {getattr(pr,'location','')} Capacity {getattr(pr,'capacity','')} Police {getattr(pr,'nearestPoliceStation','')} Hospital {getattr(pr,'nearestHospital','')} Start {getattr(pr,'commencementDate','')} Deadline {getattr(pr,'deadlineDate','')}"
        records.append(('project', pr.id, getattr(pr,'projectName',''), project_text))
```

### Step 4: Update Hybrid RAG Keywords
Modify `backend/ai_bot/hybrid_rag_service.py`:

```python
MODULE_KEYWORDS = {
    'safetyobservation': ['safety', 'observation', 'unsafe', 'ppe', 'risk', 'hazard', 'incident prevention', 'safety violation', 'near miss'],
    'incident': ['incident', 'accident', 'mishap', 'emergency', 'injury', 'damage', 'investigation', 'root cause'],
    'permit': ['permit', 'ptw', 'work permit', 'authorization', 'clearance', 'hot work', 'confined space'],
    'worker': ['worker', 'employee', 'staff', 'personnel', 'contractor', 'supervisor', 'technician'],
    'manpowerentry': ['manpower', 'attendance', 'headcount', 'workforce', 'shift', 'deployment', 'staffing'],
    'mom': ['meeting', 'minutes', 'agenda', 'mom', 'discussion', 'action items', 'decisions'],
    'project': ['project', 'site', 'construction', 'facility', 'plant', 'installation', 'development', 
                'infrastructure', 'building', 'structure', 'location', 'capacity', 'deadline', 
                'completion', 'progress', 'milestone', 'client', 'contractor', 'epc', 'scope', 'phase']
}
```

### Step 5: Frontend Integration
Update your frontend service (`frontedn/src/features/ai_bot/services/aiBotService.ts`):

```typescript
// Add new methods
async queryEnhancedRAG(query: string, searchType: 'auto' | 'project' | 'general' = 'auto'): Promise<RAGQueryResponse> {
  const response = await axios.post(`${API_BASE_URL}/rag/enhanced-query/`, { 
    query, 
    search_type: searchType 
  }, {
    headers: this.getAuthHeaders(),
    timeout: 45000,
  });
  return response.data as RAGQueryResponse;
}

async searchProjects(query: string): Promise<any> {
  const response = await axios.post(`${API_BASE_URL}/projects/search/`, { query }, {
    headers: this.getAuthHeaders(),
    timeout: 30000,
  });
  return response.data;
}

async getProjectStatistics(): Promise<any> {
  const response = await axios.get(`${API_BASE_URL}/projects/statistics/`, {
    headers: this.getAuthHeaders(),
  });
  return response.data;
}
```

## Database Optimizations

### 1. Add Database Indexes
Run these SQL commands to optimize project searches:

```sql
-- Index for project searches
CREATE INDEX IF NOT EXISTS idx_project_name_category ON authentication_project(projectName, projectCategory);
CREATE INDEX IF NOT EXISTS idx_project_location ON authentication_project(location);
CREATE INDEX IF NOT EXISTS idx_project_dates ON authentication_project(commencementDate, deadlineDate);

-- Index for related data searches
CREATE INDEX IF NOT EXISTS idx_safety_project ON safetyobservation_safetyobservation(project_id);
CREATE INDEX IF NOT EXISTS idx_incident_project ON incidentmanagement_incident(project_id);
CREATE INDEX IF NOT EXISTS idx_permit_project ON ptw_permit(project_id);
CREATE INDEX IF NOT EXISTS idx_worker_project ON worker_worker(project_id);

-- Enhanced vector search index
CREATE INDEX IF NOT EXISTS ai_bot_doc_embedding_module_idx ON ai_bot_docembedding(module) WHERE module LIKE 'project%';
```

### 2. Update Signals for Real-time Updates
Modify `backend/ai_bot/signals.py` to include more project fields:

```python
@receiver(post_save, sender=Project)
def upsert_project(sender, instance, created, **kwargs):
    from .tasks import upsert_embedding
    title = getattr(instance,'projectName','')
    # Enhanced text with all fields
    text = f"Project {title} Category {getattr(instance,'projectCategory','')} Location {getattr(instance,'location','')} Capacity {getattr(instance,'capacity','')} Police {getattr(instance,'nearestPoliceStation','')} Hospital {getattr(instance,'nearestHospital','')} Start {getattr(instance,'commencementDate','')} Deadline {getattr(instance,'deadlineDate','')}"
    upsert_embedding.delay('project', instance.id, title, text)
```

## Testing the Enhanced System

### 1. Rebuild the Index
```bash
# Run the enhanced index rebuild
curl -X POST http://localhost:8000/api/ai_bot/rag/rebuild-enhanced/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Test Project Queries
Try these enhanced queries:

- "Show me all construction projects"
- "What projects are near completion?"
- "Projects with safety issues"
- "Manufacturing facilities with high capacity"
- "Project deadlines this month"
- "Sites with recent incidents"

### 3. Test Related Data Integration
- "Project safety statistics"
- "Projects with open permits"
- "Manpower allocation by project"
- "Project incident reports"

## Expected Improvements

### 1. Search Accuracy
- **Before**: Basic keyword matching on 4 fields
- **After**: Semantic search on 12+ fields with relationships

### 2. Result Completeness  
- **Before**: Limited project info only
- **After**: Comprehensive project data with related safety, incidents, permits, workers

### 3. Query Understanding
- **Before**: 2 keywords trigger project search
- **After**: 40+ keywords with intelligent query routing

### 4. Response Quality
- **Before**: Generic snippets
- **After**: Contextual summaries with relevant metrics

## Monitoring and Maintenance

### 1. Performance Monitoring
- Track query response times
- Monitor embedding generation performance
- Watch database query efficiency

### 2. Regular Index Updates
- Schedule weekly full index rebuilds
- Monitor real-time updates via signals
- Clean up orphaned embeddings

### 3. Query Analytics
- Log popular project search terms
- Track search success rates
- Identify missing data patterns

This enhanced system will provide comprehensive, accurate, and contextual project search results that include all related data from your PostgreSQL database.
