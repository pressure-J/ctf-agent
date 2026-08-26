"""工作流路由 /api/workflows"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

@router.get("")
async def list_workflows():
    raise NotImplementedError

@router.post("")
async def create_workflow(definition: dict):
    raise NotImplementedError

@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, input_data: dict):
    raise NotImplementedError
