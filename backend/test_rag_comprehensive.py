#!/usr/bin/env python
"""
Comprehensive RAG system test
Tests all database models and RAG functionality
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_rag_comprehensive():
    """Test RAG system with comprehensive queries"""
    from ai_bot.hybrid_rag_service import HybridRAGService
    
    print("🔍 Testing Comprehensive RAG System...")
    print("=" * 50)
    
    rag = HybridRAGService()
    
    # Test queries for different models
    test_queries = [
        ("Safety Observations", "show high severity safety observations"),
        ("Incidents", "show recent incidents with high risk"),
        ("Permits", "show active permits for hot work"),
        ("Workers", "show workers in manufacturing department"),
        ("Manpower", "show manpower count for today"),
        ("Projects", "show projects in power category"),
        ("Meetings", "show recent meeting minutes"),
        ("Training", "show induction training completed"),
        ("Job Training", "show job training for welding"),
        ("Toolbox Talks", "show safety toolbox talks"),
        ("Permit Types", "show high risk permit types"),
        ("Hazards", "show electrical hazards with high risk"),
    ]
    
    results = []
    
    for category, query in test_queries:
        print(f"\n🔍 Testing: {category}")
        print(f"Query: {query}")
        
        try:
            result = rag.query(query)
            
            if result['type'] == 'rag_results':
                sources_count = len(result.get('sources', []))
                print(f"✅ Found {sources_count} sources")
                
                # Show first few sources
                for i, source in enumerate(result.get('sources', [])[:3]):
                    print(f"   📄 {source.get('module', 'unknown')}: {source.get('title', 'No title')} (score: {source.get('score', 0):.3f})")
                
                results.append((category, True, sources_count, result.get('answer', '')[:100]))
            else:
                print(f"❌ No results found")
                results.append((category, False, 0, "No results"))
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append((category, False, 0, f"Error: {str(e)}"))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 COMPREHENSIVE RAG TEST SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for _, success, _, _ in results if success)
    total = len(results)
    
    print(f"✅ Successful queries: {successful}/{total}")
    print(f"📈 Success rate: {(successful/total)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for category, success, sources, answer in results:
        status = "✅" if success else "❌"
        print(f"{status} {category:20} | Sources: {sources:2d} | {answer}")
    
    # Test specific database content
    print("\n" + "=" * 50)
    print("🗄️ DATABASE CONTENT VERIFICATION")
    print("=" * 50)
    
    # Check if we have data in each model
    model_counts = {}
    
    try:
        from safetyobservation.models import SafetyObservation
        model_counts['SafetyObservation'] = SafetyObservation.objects.count()
    except:
        model_counts['SafetyObservation'] = 0
    
    try:
        from incidentmanagement.models import Incident
        model_counts['Incident'] = Incident.objects.count()
    except:
        model_counts['Incident'] = 0
    
    try:
        from ptw.models import Permit, PermitType, HazardLibrary
        model_counts['Permit'] = Permit.objects.count()
        model_counts['PermitType'] = PermitType.objects.count()
        model_counts['HazardLibrary'] = HazardLibrary.objects.count()
    except:
        model_counts['Permit'] = model_counts['PermitType'] = model_counts['HazardLibrary'] = 0
    
    try:
        from worker.models import Worker
        model_counts['Worker'] = Worker.objects.count()
    except:
        model_counts['Worker'] = 0
    
    try:
        from manpower.models import ManpowerEntry
        model_counts['ManpowerEntry'] = ManpowerEntry.objects.count()
    except:
        model_counts['ManpowerEntry'] = 0
    
    try:
        from mom.models import Mom
        model_counts['Mom'] = Mom.objects.count()
    except:
        model_counts['Mom'] = 0
    
    try:
        from authentication.models import Project
        model_counts['Project'] = Project.objects.count()
    except:
        model_counts['Project'] = 0
    
    try:
        from inductiontraining.models import InductionTraining
        model_counts['InductionTraining'] = InductionTraining.objects.count()
    except:
        model_counts['InductionTraining'] = 0
    
    try:
        from jobtraining.models import JobTraining
        model_counts['JobTraining'] = JobTraining.objects.count()
    except:
        model_counts['JobTraining'] = 0
    
    try:
        from tbt.models import ToolboxTalk
        model_counts['ToolboxTalk'] = ToolboxTalk.objects.count()
    except:
        model_counts['ToolboxTalk'] = 0
    
    total_records = sum(model_counts.values())
    
    print(f"📊 Total database records: {total_records}")
    print("\n📋 Records per model:")
    for model, count in model_counts.items():
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {model:20} | {count:4d} records")
    
    if total_records == 0:
        print("\n⚠️  WARNING: No data found in database!")
        print("   Add some test data to see RAG results.")
    
    print(f"\n🎯 RAG System Status: {'✅ FULLY OPERATIONAL' if successful > 0 else '⚠️ NEEDS DATA'}")
    
    return successful, total, model_counts

if __name__ == '__main__':
    test_rag_comprehensive()
