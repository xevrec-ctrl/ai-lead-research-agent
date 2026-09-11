import logging
from typing import Any, AsyncIterator, Dict

from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph

from .classes.state import InputState, ResearchState
from .nodes import GroundingNode
from .nodes.briefing import Briefing
from .nodes.collector import Collector
from .nodes.curator import Curator
from .nodes.editor import Editor
from .nodes.enricher import Enricher
from .nodes.opportunity import OpportunityAnalyst
from .nodes.quality_gate import EvidenceQualityGate
from .nodes.researchers import (
    CompanyAnalyzer,
    FinancialAnalyst,
    IndustryAnalyzer,
    NewsScanner,
)

logger = logging.getLogger(__name__)


class Graph:
    def __init__(
        self,
        company=None,
        url=None,
        hq_location=None,
        industry=None,
        client_need=None,
        our_capabilities=None,
        job_id=None,
    ):
        # Initialize InputState
        self.input_state = InputState(
            company=company,
            company_url=url,
            hq_location=hq_location,
            industry=industry,
            client_need=client_need,
            our_capabilities=our_capabilities,
            job_id=job_id,
            messages=[
                SystemMessage(content="Expert researcher starting investigation")
            ],
        )

        # Initialize nodes
        self._init_nodes()
        self._build_workflow()

    def _init_nodes(self):
        """Initialize all workflow nodes"""
        self.ground = GroundingNode()
        self.financial_analyst = FinancialAnalyst()
        self.news_scanner = NewsScanner()
        self.industry_analyst = IndustryAnalyzer()
        self.company_analyst = CompanyAnalyzer()
        self.collector = Collector()
        self.curator = Curator()
        self.enricher = Enricher()
        self.briefing = Briefing()
        self.opportunity_analyst = OpportunityAnalyst()
        self.quality_gate = EvidenceQualityGate()
        self.editor = Editor()

    def _build_workflow(self):
        """Configure the state graph workflow"""
        self.workflow = StateGraph(ResearchState)

        # Add nodes with their respective processing functions
        self.workflow.add_node("grounding", self.ground.run)
        self.workflow.add_node("financial_analyst", self.financial_analyst.run)
        self.workflow.add_node("news_scanner", self.news_scanner.run)
        self.workflow.add_node("industry_analyst", self.industry_analyst.run)
        self.workflow.add_node("company_analyst", self.company_analyst.run)
        self.workflow.add_node("collector", self.collector.run)
        self.workflow.add_node("curator", self.curator.run)
        self.workflow.add_node("enricher", self.enricher.run)
        self.workflow.add_node("briefing", self.briefing.run)
        self.workflow.add_node("opportunity_analyst", self.opportunity_analyst.run)
        self.workflow.add_node("quality_gate", self.quality_gate.run)
        self.workflow.add_node("editor", self.editor.run)

        # Configure workflow edges
        self.workflow.set_entry_point("grounding")
        self.workflow.set_finish_point("editor")

        research_nodes = [
            "financial_analyst",
            "news_scanner",
            "industry_analyst",
            "company_analyst",
        ]

        # Connect grounding to all research nodes
        for node in research_nodes:
            self.workflow.add_edge("grounding", node)
            self.workflow.add_edge(node, "collector")

        # Connect remaining nodes
        self.workflow.add_edge("collector", "curator")
        self.workflow.add_edge("curator", "enricher")
        self.workflow.add_edge("enricher", "briefing")
        self.workflow.add_edge("briefing", "opportunity_analyst")
        self.workflow.add_edge("opportunity_analyst", "quality_gate")
        self.workflow.add_conditional_edges(
            "quality_gate",
            self.quality_gate.route,
            {"revise": "opportunity_analyst", "continue": "editor"},
        )

    async def run(self, thread: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Execute the research workflow"""
        compiled_graph = self.workflow.compile()

        async for state in compiled_graph.astream(self.input_state, thread):
            yield state

    def compile(self):
        graph = self.workflow.compile()
        return graph
