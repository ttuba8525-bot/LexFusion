import time
import requests
import os
from typing import Dict, Any, Generator, Tuple, Optional

# Configuration
# By default, use MOCK_MODE unless LEXFUSION_API_URL is set in environment variables
API_BASE_URL = os.getenv("LEXFUSION_API_URL", "http://localhost:8000")
MOCK_MODE = os.getenv("LEXFUSION_MOCK_MODE", "True").lower() == "true"

# Mock Data Fixtures
MOCK_DOCUMENTS = {
    "doc_merger_2026": {
        "doc_id": "doc_merger_2026",
        "filename": "Merger_Agreement_LexFusion_Acme_2026.pdf",
        "title": "Standard Merger Agreement (LexFusion Corp & Acme Holdings)",
        "pages": 24,
        "uploaded_at": "2026-08-05T10:00:00Z"
    }
}

MOCK_QA = {
    "is there a change of control clause, and what are the triggers?": {
        "answer": "Yes, Section 11.4 of the Agreement outlines the Change of Control provisions. A Change of Control is triggered if any person or group acquires more than 50% of the voting stock of LexFusion Corp, or if there is a merger, consolidation, or sale of substantially all assets, unless the pre-merger stockholders retain at least 60% of the voting power.",
        "confidence": "High",
        "citation": {
            "clause": "Section 11.4",
            "page": 14,
            "text": "Section 11.4 Change of Control triggers include (i) the acquisition by any person of beneficial ownership of 50% or more of the outstanding voting stock; (ii) the consummation of a merger, consolidation, or reorganization, unless the voting securities of the Company outstanding prior thereto continue to represent at least 60% of the combined voting power..."
        }
    },
    "what is the limit of liability under the contract?": {
        "answer": "The Agreement limits the liability of each party to a maximum cap of $5,000,000. However, this cap does not apply to breaches of confidentiality (Section 9), indemnification obligations for intellectual property infringement (Section 12.1), or losses caused by willful misconduct or gross negligence.",
        "confidence": "Medium",
        "citation": {
            "clause": "Section 15.2",
            "page": 19,
            "text": "Section 15.2 Limitation of Liability: Except for breaches of Section 9 (Confidentiality) and indemnification obligations under Section 12, in no event shall either party's aggregate liability arising out of or related to this Agreement exceed Five Million Dollars ($5,000,000)..."
        }
    },
    "what happens if a party defaults or fails to perform?": {
        "answer": "In the event of a material default or failure to perform, the non-defaulting party must provide written notice specifying the default. The defaulting party then has a 30-day cure period. If the default remains uncured after 30 days, the non-defaulting party may terminate the agreement immediately and seek legal remedies, including liquidated damages as specified in Section 13.3.",
        "confidence": "High",
        "citation": {
            "clause": "Section 13.2",
            "page": 16,
            "text": "Section 13.2 Termination on Default: Either party may terminate this Agreement immediately upon written notice if the other party fails to cure any material breach or default of its obligations hereunder within thirty (30) days after receipt of written notice describing such breach..."
        }
    },
    "are there any intellectual property indemnification exclusions?": {
        "answer": "Yes. Under Section 12.2, LexFusion's IP indemnification obligations do not apply if the infringement claim arises from: (1) Acme's modification of the software without LexFusion's approval, (2) combination of the software with third-party systems not specified in the docs, or (3) Acme's failure to implement an update or patch provided by LexFusion that would have avoided the infringement.",
        "confidence": "High",
        "citation": {
            "clause": "Section 12.2",
            "page": 15,
            "text": "Section 12.2 Indemnity Exclusions: LexFusion shall have no obligation or liability for any infringement claim based upon (a) any modification of the Deliverables by Acme or any third party; (b) combination, operation, or use of the Deliverables with products, data, or apparatus not supplied or approved by LexFusion..."
        }
    },
    "what governs the termination of this agreement?": {
        "answer": "The agreement may be terminated by mutual written consent, by either party for uncured material breach (30-day cure period), or by either party if the closing conditions are not met by the Outside Date of December 31, 2026 (Section 13.1).",
        "confidence": "High",
        "citation": {
            "clause": "Section 13.1",
            "page": 16,
            "text": "Section 13.1 Termination: This Agreement may be terminated at any time prior to the Closing: (a) by mutual written consent of LexFusion and Acme; (b) by either party if the Merger shall not have been consummated on or before December 31, 2026..."
        }
    }
}

MOCK_DEBATES = {
    "change of control: does a merger with a subsidiary trigger the 50% voting stock clause?": {
        "argument_a": "### Acme Holdings (Party A)\n\n**Position: The subsidiary merger triggers the Change of Control clause.**\n\n* **Substance of Restructuring**: A merger with a subsidiary is not merely administrative. It alters the corporate hierarchy and redirects asset control. Acme contracted with LexFusion relying on its independent operational structure.\n* **Literal Reading of Trigger**: Section 11.4(ii) defines a trigger as the 'consummation of a merger'. It does not explicitly exclude mergers with wholly-owned subsidiaries, only those where shareholders retain 60% voting power. If the subsidiary restructuring dilutes or redirects corporate governance, it satisfies the trigger threshold.\n* **Risk Exposure**: Allowing LexFusion to bypass Change of Control protections via subsidiary absorption exposes Acme to unvetted executive modifications and operational shifts.",
        "argument_b": "### LexFusion Corp (Party B)\n\n**Position: The subsidiary merger does not trigger the Change of Control clause.**\n\n* **No Third-Party Control Shift**: A Change of Control is designed to protect parties from hostile takeovers or shifts to external parties. An internal merger with a subsidiary keeps 100% of the voting control within the parent company.\n* **Shareholder Retention Clause**: Section 11.4(ii) contains an explicit exception: reorganization does not count if pre-merger voting securities continue to represent at least 60% of voting power. Since the parent's shareholders retain 100% of the ultimate voting power post-subsidiary merger, this exception is fully met.\n* **Delaware Corporate Law Precedent**: Under Delaware General Corporation Law (DGCL) § 251(g), short-form and internal reorganizations that do not affect shareholder rights are treated as non-transactional restructurings, not material changes in corporate control.",
        "verdict": {
            "ruling": "The internal merger with a subsidiary does not trigger the Change of Control provisions under Section 11.4.",
            "supported_side": "Advocate B (LexFusion Corp)",
            "neutral_meaning": "Section 11.4 governs shifts in ultimate voting power. An internal reorganization involving a wholly-owned subsidiary does not dilute the voting interest of the ultimate shareholders or introduce a third-party controller.",
            "rationale": "The plain language of Section 11.4(ii) contains a safe harbor for mergers where historical stockholders retain more than 60% of the voting control. In an internal subsidiary merger, the ultimate voting power of LexFusion Corp remains identical (100% retained). Treating this as a Change of Control would conflict with Delaware corporate precedents and the commercial intent of the parties.",
            "citation": {
                "clause": "Section 11.4(ii)",
                "page": 14,
                "text": "...unless the voting securities of the Company outstanding immediately prior thereto continue to represent at least 60% of the combined voting power..."
            }
        }
    },
    "ip indemnification: does the exclusion for 'combination of products' apply to apis?": {
        "argument_a": "### Acme Holdings (Party A)\n\n**Position: The 'combination of products' exclusion does not apply to standard APIs, meaning LexFusion must indemnify Acme.**\n\n* **API as Intended Channel**: LexFusion delivered the system with documented REST APIs. Integrating via these APIs is the standard, contractually intended way to use the product, not an unauthorized 'combination'.\n* **Failure to Exclude Specifically**: If LexFusion intended to exclude API integrations, it should have explicitly stated so. An API is an interface, not an independent 'apparatus or product' under Section 12.2.\n* **Indemnity Purpose**: Denying indemnity for standard API usage would render the IP protection clause illusory, as almost all enterprise software requires API connections to function.",
        "argument_b": "### LexFusion Corp (Party B)\n\n**Position: The 'combination of products' exclusion applies, releasing LexFusion from indemnification.**\n\n* **Broad Exclusion Language**: Section 12.2(b) excludes claims based on combination with 'products, data, or apparatus not supplied by LexFusion'. The third-party CRM/ERP system connected to the API is a separate product not supplied by LexFusion.\n* **Origin of Infringement**: The patent infringement claim targets the *data exchange mechanism* between the systems, not LexFusion's software in isolation. The infringement only exists because of the third-party combination.\n* **Control Limitations**: LexFusion cannot control how Acme configures third-party endpoints or what custom data formats are pushed through the API, making it unfair to bear indemnity risks for external configurations.",
        "verdict": {
            "ruling": "The combination exclusion does not release LexFusion from indemnification if the API integration was executed in accordance with LexFusion's own specifications and documentation.",
            "supported_side": "Advocate A (Acme Holdings)",
            "neutral_meaning": "Section 12.2(b) excludes indemnity for unauthorized combinations, but does not override LexFusion's warranty for its own documented software interfaces.",
            "rationale": "LexFusion provided and documented the REST APIs for the express purpose of system integration. An integration carried out in strict accordance with the product's official specifications is considered 'approved by LexFusion' under the contract. The exclusion in Section 12.2(b) only applies to unapproved third-party additions. Thus, Advocate A's argument holds.",
            "citation": {
                "clause": "Section 12.2(b)",
                "page": 15,
                "text": "...combination, operation, or use of the Deliverables with products, data, or apparatus not supplied or approved by LexFusion..."
            }
        }
    }
}


def upload_document(file_name: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Simulates or executes a document upload to the backend.
    """
    if MOCK_MODE:
        # Simulate processing delay
        time.sleep(1.5)
        # Create a document entry
        doc_id = f"doc_{int(time.time())}"
        doc_info = {
            "doc_id": doc_id,
            "filename": file_name,
            "title": file_name.replace(".pdf", "").replace("_", " ").title(),
            "pages": 18,
            "uploaded_at": "2026-08-05T12:00:00Z",
            "status": "success"
        }
        # Register in MOCK_DOCUMENTS dynamically
        MOCK_DOCUMENTS[doc_id] = doc_info
        return doc_info
    else:
        try:
            files = {"file": (file_name, file_bytes, "application/pdf")}
            response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}


def ask_question(question: str, doc_id: str) -> Dict[str, Any]:
    """
    Simulates or executes a grounded Q&A query.
    """
    if MOCK_MODE:
        time.sleep(1.2)  # Simulate RAG search + generation delay
        
        # Look for matching question in our fixture (case insensitive)
        query_key = question.strip().lower()
        if query_key in MOCK_QA:
            return {
                "status": "success",
                "answer": MOCK_QA[query_key]["answer"],
                "confidence": MOCK_QA[query_key]["confidence"],
                "citation": MOCK_QA[query_key]["citation"]
            }
        
        # Default fallback response for custom questions
        return {
            "status": "success",
            "answer": f"Regarding your question: '{question}', based on the uploaded legal document ({doc_id}), the agreement outlines standard operating terms. The applicable provisions require compliance with local regulations, and disputes are subject to the governing law section. If this relates to a specific transaction, the terms will become binding upon execution.",
            "confidence": "Medium",
            "citation": {
                "clause": "Section 16.4 (Miscellaneous)",
                "page": 21,
                "text": "Section 16.4 Governing Law: This Agreement shall be governed by, and construed in accordance with, the laws of the State of Delaware, without giving effect to any choice of law or conflict of law provision..."
            }
        }
    else:
        try:
            payload = {"question": question, "doc_id": doc_id}
            response = requests.post(f"{API_BASE_URL}/ask", json=payload, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "answer": f"Failed to connect to backend: {str(e)}",
                "confidence": "Low",
                "citation": None
            }


def run_debate_stream(question: str, doc_id: str) -> Generator[Tuple[str, Optional[Dict[str, Any]]], None, None]:
    """
    Yields status updates sequentially, and yields the final debate result at the end.
    This creates an engaging courtroom sequence for the flagship debate feature.
    """
    # We clean up the query key to check in our mock debate dict
    query_key = question.strip().lower()
    
    # Generate mock result or default fallback
    if query_key in MOCK_DEBATES:
        debate_result = MOCK_DEBATES[query_key]
    else:
        # Default fallback debate
        debate_result = {
            "argument_a": f"### Advocate A (Party A)\n\n**Position: The clause should be interpreted strictly in favor of Party A.**\n\n* **Operational Impact**: A broad reading protects the commercial interests of Party A against unilateral changes.\n* **Strict Construction**: Ambiguities in contracts are traditionally interpreted against the drafting party.\n* **Indemnity Safeguard**: Under the current wording of the clause, Party A maintains rights to indemnification because no exclusions explicitly cover this setup.",
            "argument_b": f"### Advocate B (Party B)\n\n**Position: The clause should be interpreted broadly, favoring Party B.**\n\n* **Commercial Realities**: Party B's exposure is limited by the liability caps agreed upon in Section 15.\n* **Integration Scope**: The clause was negotiated to restrict liability for unapproved modifications. Party A's custom code falls outside the approved product specification.\n* **Force Majeure**: Unforeseeable external actions by vendors relieve Party B of performance duties in this specific scenario.",
            "verdict": {
                "ruling": f"The argument regarding '{question}' is resolved in favor of Party B, subject to limitation caps.",
                "supported_side": "Advocate B (Party B)",
                "neutral_meaning": f"The clause is meant to allocate risk during integrations. Standard terms protect the vendor from unauthorized alterations unless explicitly signed off.",
                "rationale": "While Advocate A presents a strong argument regarding standard operations, the contract explicitly limits liability for external integrations under Section 12.2. Therefore, Advocate B's defense against full indemnification holds weight, capped at the liability limit of Section 15.2.",
                "citation": {
                    "clause": "Section 12.2 & 15.2",
                    "page": 17,
                    "text": "...claims arising from unapproved configurations are excluded from indemnity, governed by the liability caps of Section 15.2..."
                }
            }
        }

    if MOCK_MODE:
        yield "Advocate A is analyzing the contract and drafting the argument for Party A...", None
        time.sleep(1.5)
        yield "Advocate B is assessing opposing arguments and preparing the rebuttal for Party B...", None
        time.sleep(1.5)
        yield "Neutral Judge is weighing advocate arguments and drafting the final verdict...", None
        time.sleep(1.5)
        yield "Verdict rendered!", debate_result
    else:
        # For live mode, we make a blocking call, but still simulate stages in the UI,
        # or we just call the endpoint. To keep the UI engaging, we yield steps first,
        # then perform the network request, or stream if the backend supports it.
        yield "Advocate A is formulating the opening argument...", None
        time.sleep(0.5)
        yield "Advocate B is formulating the response...", None
        time.sleep(0.5)
        yield "Neutral Judge is evaluating and rendering the final decision...", None
        
        try:
            payload = {"question": question, "doc_id": doc_id}
            response = requests.post(f"{API_BASE_URL}/debate", json=payload, timeout=20)
            response.raise_for_status()
            yield "Verdict rendered!", response.json()
        except Exception as e:
            # Fallback error response
            err_result = {
                "argument_a": "Error loading Advocate A argument.",
                "argument_b": "Error loading Advocate B argument.",
                "verdict": {
                    "ruling": f"Failed to execute debate: {str(e)}",
                    "supported_side": "None",
                    "neutral_meaning": "N/A",
                    "rationale": "An error occurred while connecting to the RAG backend.",
                    "citation": None
                }
            }
            yield "Failed to render verdict.", err_result
