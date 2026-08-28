"""工作流路由"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict, Any
from web.deps import database, security, WorkflowDefinition, execute_workflow_engine

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

@router.get("")
async def list_workflows(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"workflows": database.list_workflows()}

@router.post("")
async def create_workflow(workflow: WorkflowDefinition,
                          credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"workflow_id": database.create_workflow(workflow.model_dump())}

@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, input_data: Dict[str, Any],
                           credentials: HTTPAuthorizationCredentials = Depends(security)):
    workflow = database.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return {"result": execute_workflow_engine(workflow, input_data)}
