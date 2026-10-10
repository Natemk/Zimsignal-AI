import sys
import os
sys.path.append(os.path.abspath("."))

from retrieval.rag_chain import query_rag_pipeline

def test_acceptance_gate():
    print("🚀 Running Acceptance Gate Tests...\n")
    
    # 1. Valid Query Test
    valid_query = "What is artificial intelligence?"
    print(f"Test 1: Valid Query -> '{valid_query}'")
    res_valid = query_rag_pipeline(valid_query, source_tier_filter="secondary_verified")
    
    assert len(res_valid["retrieved_chunks"]) > 0, "Failed: Should retrieve document chunks."
    assert len(res_valid["source_urls"]) > 0, "Failed: Source URLs must be present for citations."
    print(f"✅ PASSED - Retrieved {len(res_valid['retrieved_chunks'])} chunk(s) from {res_valid['source_urls']}")
    
    # 2. Rejection Test (Query with non-existent source filter)
    out_of_bounds_query = "What is quantum gravity?"
    print(f"\nTest 2: Out-of-Bounds/Missing Evidence Query -> '{out_of_bounds_query}'")
    res_rejected = query_rag_pipeline(out_of_bounds_query, source_tier_filter="non_existent_tier")
    
    assert len(res_rejected["retrieved_chunks"]) == 0, "Failed: Should return zero chunks."
    assert res_rejected["answer"] == "Insufficient evidence available in retrieved documents to answer this question.", "Failed: Must explicitly reject."
    print(f"✅ PASSED - Successfully triggered Appendix D evidence rejection response.")

    print("\n🎉 ALL ACCEPTANCE GATE TESTS PASSED!")

if __name__ == "__main__":
    test_acceptance_gate()
