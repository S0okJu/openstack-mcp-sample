#!/usr/bin/env python3
"""
OpenStack MCP Class-Based Server
클래스 기반 구조화된 OpenStack MCP 서버
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

import openstack
from openstack import connection
from fastmcp import FastMCP, Context


class OpenStackMCP:
    """OpenStack MCP Server 클래스"""
    
    def __init__(self, name: str = 'openstack-mcp'):
        """
        OpenStack MCP 서버 초기화
        
        Args:
            name: MCP 서버 이름
        """
        self.server = FastMCP(name)  # name=mcp 오타 수정
        self.conn = self._connect_openstack()
        self._setup_tools()
        
    def _connect_openstack(self) -> connection.Connection:
        """OpenStack 연결 설정"""
        try:
            # 환경변수를 통한 연결
            if all(key in os.environ for key in ['OS_AUTH_URL', 'OS_USERNAME', 'OS_PASSWORD', 'OS_PROJECT_NAME']):
                conn = openstack.connect(
                    auth_url=os.environ['OS_AUTH_URL'],
                    project_name=os.environ['OS_PROJECT_NAME'],
                    username=os.environ['OS_USERNAME'],
                    password=os.environ['OS_PASSWORD'],
                    user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME', 'Default'),
                    project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default'),
                    region_name=os.environ.get('OS_REGION_NAME', 'RegionOne'),
                    interface=os.environ.get('OS_INTERFACE', 'public'),
                    identity_api_version=os.environ.get('OS_IDENTITY_API_VERSION', '3')
                )
            else:
                # clouds.yaml을 통한 연결
                conn = openstack.connect(cloud=os.environ.get('OS_CLOUD', 'openstack'))
            
            # 연결 테스트
            conn.authorize()
            print("✅ OpenStack connection established successfully")
            return conn
            
        except Exception as e:
            print(f"❌ Failed to connect to OpenStack: {e}")
            raise
    
    def _setup_tools(self):
        """모든 MCP 툴들을 등록"""
        
        # Nova (Compute) 관련 툴들
        @self.server.tool()
        def nova_list(detailed: bool = False, status: Optional[str] = None) -> str:
            """
            Nova 서버 목록 조회
            
            Args:
                detailed: 상세 정보 포함 여부
                status: 상태별 필터링 (ACTIVE, SHUTOFF, ERROR 등)
            """
            return self.nova_list_impl(detailed, status)
        
        @self.server.tool()
        def nova_show(server_id: str) -> str:
            """
            특정 서버의 상세 정보 조회
            
            Args:
                server_id: 서버 ID 또는 이름
            """
            return self.nova_show_impl(server_id)
        
        @self.server.tool()
        def nova_console_log(server_id: str, length: int = 50) -> str:
            """
            서버 콘솔 로그 조회
            
            Args:
                server_id: 서버 ID 또는 이름
                length: 조회할 라인 수
            """
            return self.nova_console_log_impl(server_id, length)
        
        # AI 분석 관련 툴들
        @self.server.tool()
        async def analyze_instance_errors(server_id: str, ctx: Context, log_lines: int = 200) -> str:
            """
            AI를 활용한 인스턴스 에러 분석
            
            Args:
                server_id: 서버 ID 또는 이름
                ctx: FastMCP Context
                log_lines: 분석할 로그 라인 수
            """
            return await self.analyze_instance_errors_impl(server_id, log_lines, ctx)
        
        @self.server.tool()
        async def bulk_infrastructure_analysis(ctx: Context,
                                             status_filter: Optional[str] = None, 
                                             max_instances: int = 10) -> str:
            """
            인프라 전체 일괄 분석
            
            Args:
                ctx: FastMCP Context
                status_filter: 상태별 필터링
                max_instances: 분석할 최대 인스턴스 수
            """
            return await self.bulk_infrastructure_analysis_impl(status_filter, max_instances, ctx)
        
        @self.server.tool()
        async def emergency_recovery_plan(server_id: str, ctx: Context) -> str:
            """
            AI 기반 응급 복구 계획 생성
            
            Args:
                server_id: 서버 ID 또는 이름
                ctx: FastMCP Context
            """
            return await self.emergency_recovery_plan_impl(server_id, ctx)
        
        @self.server.tool()
        async def custom_question_analysis(server_id: str, question: str, ctx: Context) -> str:
            """
            사용자 정의 질문으로 AI 분석
            
            Args:
                server_id: 서버 ID 또는 이름
                question: 사용자 질문
                ctx: FastMCP Context
            """
            return await self.custom_question_analysis_impl(server_id, question, ctx)
        
        # 기타 OpenStack 서비스 툴들
        @self.server.tool()
        def glance_list_images(public_only: bool = False) -> str:
            """이미지 목록 조회"""
            return self.glance_list_images_impl(public_only)
        
        @self.server.tool()
        def neutron_list_networks(external_only: bool = False) -> str:
            """네트워크 목록 조회"""
            return self.neutron_list_networks_impl(external_only)
        
        @self.server.tool()
        def nova_list_flavors(public_only: bool = False) -> str:
            """Flavor 목록 조회"""
            return self.nova_list_flavors_impl(public_only)
    
    # Nova 구현 메서드들
    def nova_list_impl(self, detailed: bool = False, status: Optional[str] = None) -> str:
        """Nova 서버 목록 조회 구현"""
        try:
            filters = {}
            if status:
                filters["status"] = status.upper()
            
            servers = list(self.conn.compute.servers(detailed=detailed, **filters))
            
            if not servers:
                return "❌ No servers found"
            
            result = []
            for server in servers:
                if detailed:
                    server_info = {
                        "id": server.id,
                        "name": server.name,
                        "status": server.status,
                        "flavor": server.flavor.get("original_name", server.flavor.get("id")),
                        "image": server.image.get("original_name", server.image.get("id")) if server.image else "N/A",
                        "created": str(server.created_at),
                        "updated": str(server.updated_at),
                        "addresses": server.addresses,
                        "power_state": getattr(server, 'power_state', 'N/A'),
                        "vm_state": getattr(server, 'vm_state', 'N/A')
                    }
                else:
                    server_info = {
                        "id": server.id,
                        "name": server.name,
                        "status": server.status
                    }
                result.append(server_info)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return f"❌ Error listing servers: {str(e)}"
    
    def nova_show_impl(self, server_id: str) -> str:
        """서버 상세 정보 조회 구현"""
        try:
            server = self.conn.compute.get_server(server_id)
            if not server:
                return f"❌ Server not found: {server_id}"
            
            server_info = {
                "id": server.id,
                "name": server.name,
                "status": server.status,
                "flavor": server.flavor,
                "image": server.image,
                "created": str(server.created_at),
                "updated": str(server.updated_at),
                "addresses": server.addresses,
                "metadata": server.metadata,
                "fault": server.fault,
                "power_state": getattr(server, 'power_state', 'N/A'),
                "task_state": getattr(server, 'task_state', 'N/A'),
                "vm_state": getattr(server, 'vm_state', 'N/A')
            }
            
            return json.dumps(server_info, indent=2, ensure_ascii=False, default=str)
            
        except Exception as e:
            return f"❌ Error getting server details: {str(e)}"
    
    def nova_console_log_impl(self, server_id: str, length: int = 50) -> str:
        """콘솔 로그 조회 구현"""
        try:
            server = self.conn.compute.get_server(server_id)
            if not server:
                return f"❌ Server not found: {server_id}"
            
            console_log = self.conn.compute.get_server_console_output(server, length=length)
            
            if not console_log:
                return f"❌ No console log available for {server.name}"
            
            return f"📋 Console log for {server.name} (last {length} lines):\n\n{console_log}"
            
        except Exception as e:
            return f"❌ Error getting console log: {str(e)}"
    
    # AI 분석 메서드들
    def _extract_error_patterns(self, log_content: str) -> Dict[str, Any]:
        """에러 패턴 추출"""
        if not log_content:
            return {"has_errors": False, "error_lines": []}
        
        error_indicators = [
            r'error', r'fail', r'panic', r'critical', r'fatal', r'emergency', 
            r'alert', r'warning', r'exception', r'segfault', r'oops', r'bug',
            r'cannot', r'unable', r'timeout', r'refused', r'denied'
        ]
        
        pattern = '|'.join(error_indicators)
        error_lines = []
        log_lines = log_content.split('\n')
        
        for i, line in enumerate(log_lines):
            if re.search(pattern, line, re.IGNORECASE):
                context = {
                    "line_number": i + 1,
                    "content": line.strip(),
                    "context_before": [l.strip() for l in log_lines[max(0, i-2):i] if l.strip()],
                    "context_after": [l.strip() for l in log_lines[i+1:min(len(log_lines), i+3)] if l.strip()]
                }
                error_lines.append(context)
        
        return {
            "has_errors": len(error_lines) > 0,
            "error_count": len(error_lines),
            "error_lines": error_lines[:15],
            "total_lines": len(log_lines)
        }
    
    async def analyze_instance_errors_impl(self, server_id: str, log_lines: int, ctx: Context) -> str:
        """인스턴스 에러 분석 구현"""
        try:
            await ctx.info(f"🔍 Analyzing server {server_id}...")
            
            server = self.conn.compute.get_server(server_id)
            if not server:
                return f"❌ Server not found: {server_id}"
            
            console_log = self.conn.compute.get_server_console_output(server, length=log_lines)
            if not console_log:
                return f"❌ No console log available for server: {server.name}"
            
            error_analysis = self._extract_error_patterns(console_log)
            
            if not error_analysis["has_errors"]:
                return f"✅ No obvious errors found in {server.name} console log. Instance appears healthy."
            
            await ctx.info(f"🚨 Found {error_analysis['error_count']} potential errors. Requesting AI analysis...")
            
            # AI 분석을 위한 구조화된 프롬프트 생성
            analysis_prompt = f"""
당신은 OpenStack 전문가입니다. 다음 인스턴스의 콘솔 로그를 분석하고 에러 진단 및 해결책을 제공해주세요.

**인스턴스 정보:**
- ID: {server.id}
- 이름: {server.name}  
- 상태: {server.status}
- 생성일: {server.created_at}
- Flavor: {json.dumps(server.flavor, indent=2) if server.flavor else "N/A"}
- Image: {json.dumps(server.image, indent=2) if server.image else "N/A"}

**에러 분석 결과:**
- 총 에러 라인: {error_analysis['error_count']}개
- 로그 총 라인: {error_analysis['total_lines']}개

**주요 에러 라인들:**
"""

            # 에러 상세 정보 추가
            for i, error_line in enumerate(error_analysis["error_lines"][:10], 1):
                analysis_prompt += f"\nError {i} (Line {error_line['line_number']}):\n"
                analysis_prompt += f"  내용: {error_line['content']}\n"
                if error_line['context_before']:
                    analysis_prompt += f"  이전: {' | '.join(error_line['context_before'][-2:])}\n"
                if error_line['context_after']:
                    analysis_prompt += f"  이후: {' | '.join(error_line['context_after'][:2])}\n"

            analysis_prompt += f"""

**전체 로그 (마지막 부분):**
```
{console_log[-1500:] if len(console_log) > 1500 else console_log}
```

다음 형식으로 분석해주세요:

1. **🔍 에러 진단**: 발견된 주요 문제점들
2. **🎯 근본 원인**: 가능성이 높은 원인 분석  
3. **⚡ 즉시 해결책**: 바로 실행 가능한 OpenStack 명령어들
4. **🔧 상세 해결 방법**: 단계별 상세 가이드
5. **🛡️ 예방 조치**: 재발 방지 방법
6. **⚠️ 주의사항**: 해결 과정에서 주의할 점

구체적이고 실행 가능한 OpenStack CLI 명령어를 포함해서 답변해주세요.
"""

            # LLM에게 분석 요청
            ai_response = await ctx.sample(analysis_prompt)
            
            await ctx.info("✅ AI analysis completed!")
            
            return f"""# 🤖 AI 기반 OpenStack 인스턴스 에러 분석 결과

## 서버 정보
- **ID**: {server.id}
- **이름**: {server.name}
- **상태**: {server.status}
- **에러 수**: {error_analysis['error_count']}개

## AI 분석 결과

{ai_response.content[0].text if ai_response.content else "AI 분석을 완료할 수 없습니다."}

---
*분석 시간: {datetime.now().isoformat()}*
"""
            
        except Exception as e:
            await ctx.error(f"Error analyzing server {server_id}: {str(e)}")
            return f"❌ Error analyzing server {server_id}: {str(e)}"
    
    async def bulk_infrastructure_analysis_impl(self, status_filter: Optional[str], max_instances: int, ctx: Context) -> str:
        """인프라 전체 분석 구현"""
        try:
            await ctx.info(f"🔍 Starting bulk infrastructure analysis...")
            
            filters = {}
            if status_filter:
                filters["status"] = status_filter.upper()
            
            servers = list(self.conn.compute.servers(**filters))[:max_instances]
            
            if not servers:
                return "❌ No servers found for analysis"
            
            # 각 인스턴스의 간단한 분석
            bulk_data = {
                "summary": {
                    "total_analyzed": len(servers),
                    "filter_applied": status_filter or "none",
                    "analysis_timestamp": datetime.now().isoformat()
                },
                "instances": []
            }
            
            problematic_instances = []
            
            for server in servers:
                try:
                    await ctx.info(f"Analyzing {server.name}...")
                    
                    console_log = self.conn.compute.get_server_console_output(server, length=100)
                    error_analysis = self._extract_error_patterns(console_log) if console_log else {"has_errors": False}
                    
                    instance_data = {
                        "id": server.id,
                        "name": server.name,
                        "status": server.status,
                        "has_errors": error_analysis.get("has_errors", False),
                        "error_count": error_analysis.get("error_count", 0),
                        "fault": server.fault,
                        "created": str(server.created_at),
                        "sample_errors": [
                            err["content"] for err in error_analysis.get("error_lines", [])[:3]
                        ] if error_analysis.get("has_errors") else []
                    }
                    
                    bulk_data["instances"].append(instance_data)
                    
                    if error_analysis.get("has_errors") or server.status == "ERROR":
                        problematic_instances.append(instance_data)
                    
                except Exception as e:
                    bulk_data["instances"].append({
                        "id": server.id,
                        "name": server.name,
                        "status": server.status,
                        "analysis_error": str(e)
                    })

            # AI에게 전체 인프라 분석 요청
            if problematic_instances:
                await ctx.info("🤖 Requesting AI analysis for infrastructure-level insights...")
                
                infrastructure_prompt = f"""
OpenStack 환경의 여러 인스턴스들을 일괄 분석한 결과입니다. 
전체적인 인프라 관점에서 문제점과 해결책을 제시해주세요.

**분석 결과 요약:**
- 총 분석 인스턴스: {len(servers)}개
- 문제가 있는 인스턴스: {len(problematic_instances)}개
- 필터: {status_filter or "없음"}

**문제가 있는 인스턴스들:**
{json.dumps(problematic_instances, indent=2, ensure_ascii=False)}

다음 관점에서 분석해주세요:

1. **🏗️ 인프라 레벨 이슈**: 공통적인 패턴이나 시스템 문제
2. **📊 우선순위**: 어떤 인스턴스를 먼저 처리해야 하는지
3. **🔄 자동화 제안**: 반복적인 문제 해결을 위한 자동화 방안
4. **📈 모니터링 강화**: 추가로 모니터링해야 할 메트릭들
5. **🚨 에스컬레이션**: 상위 팀에 보고해야 할 사항들

실행 가능한 OpenStack 명령어와 스크립트를 포함해서 답변해주세요.
"""

                ai_response = await ctx.sample(infrastructure_prompt)
                ai_analysis = ai_response.content[0].text if ai_response.content else "AI 분석을 완료할 수 없습니다."
            else:
                ai_analysis = "✅ 모든 인스턴스가 정상 상태입니다. 특별한 조치가 필요하지 않습니다."

            await ctx.info("✅ Bulk analysis completed!")
            
            return f"""# 🏗️ OpenStack 인프라 전체 분석 결과

## 📊 분석 요약
- **총 인스턴스**: {len(servers)}개
- **문제 인스턴스**: {len(problematic_instances)}개
- **정상 인스턴스**: {len(servers) - len(problematic_instances)}개

## 🤖 AI 인프라 분석

{ai_analysis}

## 📋 상세 인스턴스 목록

{json.dumps(bulk_data, indent=2, ensure_ascii=False)}

---
*분석 시간: {datetime.now().isoformat()}*
"""
            
        except Exception as e:
            await ctx.error(f"Error in bulk analysis: {str(e)}")
            return f"❌ Error in bulk analysis: {str(e)}"
    
    async def emergency_recovery_plan_impl(self, server_id: str, ctx: Context) -> str:
        """응급 복구 계획 생성 구현"""
        try:
            await ctx.info(f"🚨 Creating emergency recovery plan for {server_id}...")
            
            server = self.conn.compute.get_server(server_id)
            if not server:
                return f"❌ Server not found: {server_id}"
            
            console_log = self.conn.compute.get_server_console_output(server, length=300)
            error_analysis = self._extract_error_patterns(console_log) if console_log else {"has_errors": False}
            
            recovery_prompt = f"""
OpenStack 인스턴스에 심각한 문제가 발생했습니다. 응급 복구 절차를 생성해주세요.

**인스턴스 정보:**
- ID: {server.id}
- 이름: {server.name}
- 현재 상태: {server.status}
- Power State: {getattr(server, 'power_state', 'N/A')}
- VM State: {getattr(server, 'vm_state', 'N/A')}
- Task State: {getattr(server, 'task_state', 'N/A')}
- Fault: {server.fault if server.fault else "없음"}

**에러 분석:**
- 에러 발견: {"예" if error_analysis.get("has_errors") else "아니오"}
- 에러 수: {error_analysis.get("error_count", 0)}개

**최근 로그 (마지막 500자):**
```
{console_log[-500:] if console_log else "로그 없음"}
```

다음 형식으로 응급 복구 계획을 작성해주세요:

1. **🚨 즉시 실행 항목** (5분 이내)
2. **⚡ 단기 복구 절차** (30분 이내)  
3. **🔧 장기 해결 방안** (1시간 이내)
4. **📋 체크리스트** (각 단계별 확인사항)
5. **🆘 에스컬레이션 기준** (언제 상위팀에 보고할지)
6. **📞 비상 연락처** (필요한 팀들)

모든 명령어는 OpenStack CLI 기준으로 작성해주세요.
"""

            ai_response = await ctx.sample(recovery_prompt)
            await ctx.info("✅ Emergency recovery plan generated!")
            
            return f"""# 🚨 AI 기반 응급 복구 계획

## 인스턴스 정보
- **서버**: {server.name} ({server.id})
- **현재 상태**: {server.status}
- **생성 시간**: {datetime.now().isoformat()}

## 🤖 AI 생성 복구 계획

{ai_response.content[0].text if ai_response.content else "복구 계획을 생성할 수 없습니다."}

## ⚠️ 중요 안내
- 복구 작업 전에 반드시 스냅샷 생성을 고려하세요
- 각 단계 실행 후 결과를 확인하세요
- 문제가 해결되지 않으면 즉시 에스컬레이션하세요

---
*계획 생성 시간: {datetime.now().isoformat()}*
"""
            
        except Exception as e:
            await ctx.error(f"Error creating recovery plan: {str(e)}")
            return f"❌ Error creating recovery plan: {str(e)}"
    
    async def custom_question_analysis_impl(self, server_id: str, question: str, ctx: Context) -> str:
        """사용자 정의 질문 분석 구현"""
        try:
            await ctx.info(f"🤔 Processing custom question about {server_id}...")
            
            server = self.conn.compute.get_server(server_id)
            if not server:
                return f"❌ Server not found: {server_id}"
            
            console_log = self.conn.compute.get_server_console_output(server, length=250)
            
            custom_prompt = f"""
OpenStack 전문가로서 다음 인스턴스에 대한 사용자의 질문에 답변해주세요.

**인스턴스 정보:**
- ID: {server.id}
- 이름: {server.name}
- 상태: {server.status}
- Flavor: {json.dumps(server.flavor, indent=2) if server.flavor else "N/A"}

**사용자 질문:**
{question}

**관련 콘솔 로그:**
```
{console_log if console_log else "로그 없음"}
```

위 정보를 바탕으로 사용자의 질문에 대해 상세하고 실용적인 답변을 제공해주세요.
가능하면 구체적인 OpenStack 명령어나 해결 방법을 포함해주세요.
"""

            ai_response = await ctx.sample(custom_prompt)
            await ctx.info("✅ Custom analysis completed!")
            
            return f"""# 🤔 사용자 정의 질문 분석 결과

## 질문
> {question}

## 인스턴스 정보
- **서버**: {server.name} ({server.id})
- **상태**: {server.status}

## 🤖 AI 답변

{ai_response.content[0].text if ai_response.content else "답변을 생성할 수 없습니다."}

---
*분석 시간: {datetime.now().isoformat()}*
"""
            
        except Exception as e:
            await ctx.error(f"Error processing custom question: {str(e)}")
            return f"❌ Error processing question: {str(e)}"
    
    # 기타 OpenStack 서비스 구현 메서드들
    def glance_list_images_impl(self, public_only: bool) -> str:
        """이미지 목록 조회 구현"""
        try:
            filters = {}
            if public_only:
                filters["visibility"] = "public"
            
            images = list(self.conn.image.images(**filters))
            
            if not images:
                return "❌ No images found"
            
            result = []
            for image in images:
                image_info = {
                    "id": image.id,
                    "name": image.name,
                    "status": image.status,
                    "visibility": image.visibility,
                    "size": image.size,
                    "created": str(image.created_at),
                    "updated": str(image.updated_at)
                }
                result.append(image_info)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return f"❌ Error listing images: {str(e)}"
    
    def neutron_list_networks_impl(self, external_only: bool) -> str:
        """네트워크 목록 조회 구현"""
        try:
            filters = {}
            if external_only:
                filters["router:external"] = True
            
            networks = list(self.conn.network.networks(**filters))
            
            if not networks:
                return "❌ No networks found"
            
            result = []
            for network in networks:
                network_info = {
                    "id": network.id,
                    "name": network.name,
                    "status": network.status,
                    "admin_state_up": network.is_admin_state_up,
                    "external": network.is_router_external,
                    "shared": network.is_shared,
                    "subnets": network.subnet_ids
                }
                result.append(network_info)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return f"❌ Error listing networks: {str(e)}"
    
    def nova_list_flavors_impl(self, public_only: bool) -> str:
        """Flavor 목록 조회 구현"""
        try:
            filters = {}
            if public_only:
                filters["is_public"] = True
            
            flavors = list(self.conn.compute.flavors(**filters))
            
            if not flavors:
                return "❌ No flavors found"
            
            result = []
            for flavor in flavors:
                flavor_info = {
                    "id": flavor.id,
                    "name": flavor.name,
                    "vcpus": flavor.vcpus,
                    "ram": flavor.ram,
                    "disk": flavor.disk,
                    "ephemeral": flavor.ephemeral,
                    "swap": flavor.swap,
                    "is_public": flavor.is_public
                }
                result.append(flavor_info)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return f"❌ Error listing flavors: {str(e)}"
    
    def run(self):
        """MCP 서버 실행"""
        print(f"🚀 Starting OpenStack MCP Server...")
        self.server.run()


# 사용 예시
if __name__ == "__main__":
    # OpenStack MCP 서버 생성 및 실행
    openstack_mcp = OpenStackMCP(name="openstack-ai-analyzer")
    openstack_mcp.run()