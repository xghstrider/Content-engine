"""
Template management implementation
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles

from content_engine.config.settings import get_settings
from content_engine.models.templates import Template, TemplateCategory, TemplateType, TemplateVariable
from content_engine.templates.renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class TemplateManager:
    """Template management system"""
    
    def __init__(
        self,
        template_dirs: Optional[List[Union[str, Path]]] = None,
    ):
        self.settings = get_settings()
        self.renderer = TemplateRenderer()
        
        # Initialize template directories
        if template_dirs is None:
            template_dirs = self.settings.template_dirs
        
        self.template_dirs = [Path(d) for d in template_dirs]
        self._templates: Dict[str, Template] = {}
        self._loaded = False
    
    async def initialize(self) -> None:
        """Initialize the template manager by loading all templates"""
        if self._loaded:
            return
        
        logger.info("Loading templates...")
        
        for template_dir in self.template_dirs:
            if template_dir.exists() and template_dir.is_dir():
                await self._load_templates_from_dir(template_dir)
        
        self._loaded = True
        logger.info(f"Loaded {len(self._templates)} templates")
    
    async def _load_templates_from_dir(self, template_dir: Path) -> None:
        """Load templates from a directory"""
        # Load JSON template files
        for template_file in template_dir.glob("*.json"):
            try:
                async with aiofiles.open(template_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    template_data = json.loads(content)
                    
                    template = Template(**template_data)
                    template.id = template_file.stem
                    
                    self._templates[template.id] = template
                    logger.debug(f"Loaded template: {template.id}")
                    
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load template {template_file.name}: {e}")
        
        # Load text template files
        for template_file in template_dir.glob("*.txt"):
            try:
                async with aiofiles.open(template_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    
                    template = Template(
                        id=template_file.stem,
                        name=template_file.stem.replace('_', ' ').title(),
                        description=f"Template from {template_file.name}",
                        template_type=TemplateType.TEXT,
                        content=content,
                        category=TemplateCategory.SOCIAL_MEDIA,
                    )
                    
                    self._templates[template.id] = template
                    logger.debug(f"Loaded text template: {template.id}")
                    
            except IOError as e:
                logger.warning(f"Failed to load template {template_file.name}: {e}")
    
    async def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template by ID"""
        if not self._loaded:
            await self.initialize()
        
        return self._templates.get(template_id)
    
    async def get_templates_by_category(
        self,
        category: TemplateCategory,
    ) -> List[Template]:
        """Get all templates in a category"""
        if not self._loaded:
            await self.initialize()
        
        return [t for t in self._templates.values() if t.category == category]
    
    async def get_templates_by_type(
        self,
        template_type: TemplateType,
    ) -> List[Template]:
        """Get all templates of a specific type"""
        if not self._loaded:
            await self.initialize()
        
        return [t for t in self._templates.values() if t.template_type == template_type]
    
    async def search_templates(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Template]:
        """Search templates by name or description"""
        if not self._loaded:
            await self.initialize()
        
        query_lower = query.lower()
        results = []
        
        for template in self._templates.values():
            if (query_lower in template.name.lower() or 
                query_lower in template.description.lower() or
                query_lower in template.id.lower()):
                results.append(template)
                
                if len(results) >= limit:
                    break
        
        return results
    
    async def list_templates(
        self,
        category: Optional[TemplateCategory] = None,
        template_type: Optional[TemplateType] = None,
    ) -> List[Template]:
        """List all available templates with optional filters"""
        if not self._loaded:
            await self.initialize()
        
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if template_type:
            templates = [t for t in templates if t.template_type == template_type]
        
        return templates
    
    async def create_template(
        self,
        template: Template,
        save_to_disk: bool = True,
    ) -> Template:
        """Create a new template"""
        if not template.id:
            template.id = self._generate_template_id(template.name)
        
        self._templates[template.id] = template
        
        if save_to_disk:
            await self._save_template_to_disk(template)
        
        return template
    
    async def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any],
        save_to_disk: bool = True,
    ) -> Optional[Template]:
        """Update an existing template"""
        template = await self.get_template(template_id)
        
        if not template:
            return None
        
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        if save_to_disk:
            await self._save_template_to_disk(template)
        
        return template
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        template = await self.get_template(template_id)
        
        if not template:
            return False
        
        del self._templates[template_id]
        
        # Delete from disk
        for template_dir in self.template_dirs:
            template_file = template_dir / f"{template_id}.json"
            if template_file.exists():
                try:
                    await template_file.unlink()
                    return True
                except IOError as e:
                    logger.error(f"Failed to delete template file {template_file}: {e}")
                    return False
        
        return True
    
    async def render_template(
        self,
        template_id: str,
        variables: Dict[str, Any],
    ) -> str:
        """Render a template with variables"""
        template = await self.get_template(template_id)
        
        if not template:
            raise ValueError(f"Template '{template_id}' not found")
        
        return self.renderer.render(template, variables)
    
    async def render_template_string(
        self,
        template_content: str,
        variables: Dict[str, Any],
        template_type: str = "text",
    ) -> str:
        """Render a template string with variables"""
        return self.renderer.render_string(template_content, variables, template_type)
    
    async def _save_template_to_disk(self, template: Template) -> None:
        """Save a template to disk"""
        template_dir = self.template_dirs[0]  # Save to first directory
        template_dir.mkdir(parents=True, exist_ok=True)
        
        template_file = template_dir / f"{template.id}.json"
        
        try:
            async with aiofiles.open(template_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(template.model_dump(), ensure_ascii=False, indent=2))
                logger.debug(f"Saved template to {template_file}")
                
        except IOError as e:
            logger.error(f"Failed to save template {template.id}: {e}")
    
    def _generate_template_id(self, name: str) -> str:
        """Generate a unique template ID from a name"""
        import hashlib
        import time
        
        # Create a unique ID based on name and timestamp
        unique_str = f"{name}_{time.time()}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]
    
    async def import_templates(
        self,
        templates: List[Dict[str, Any]],
    ) -> int:
        """Import multiple templates"""
        count = 0
        
        for template_data in templates:
            template = Template(**template_data)
            await self.create_template(template)
            count += 1
        
        return count
    
    async def export_templates(
        self,
        category: Optional[TemplateCategory] = None,
    ) -> List[Dict[str, Any]]:
        """Export templates as dictionaries"""
        templates = await self.list_templates(category=category)
        return [t.model_dump() for t in templates]
    
    async def get_popular_templates(self, limit: int = 10) -> List[Template]:
        """Get the most popular templates"""
        if not self._loaded:
            await self.initialize()
        
        templates = sorted(
            self._templates.values(),
            key=lambda t: t.popularity_score,
            reverse=True,
        )[:limit]
        
        return templates
    
    async def get_recently_used_templates(self, limit: int = 10) -> List[Template]:
        """Get recently used templates"""
        if not self._loaded:
            await self.initialize()
        
        templates = sorted(
            self._templates.values(),
            key=lambda t: t.updated_at or t.created_at,
            reverse=True,
        )[:limit]
        
        return templates
    
    async def increment_usage(self, template_id: str) -> None:
        """Increment the usage count for a template"""
        template = await self.get_template(template_id)
        
        if template:
            template.usage_count += 1
            # Simple popularity calculation
            template.popularity_score = min(1.0, template.usage_count * 0.1)
            await self._save_template_to_disk(template)
