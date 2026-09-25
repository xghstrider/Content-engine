"""
Template rendering implementation
"""

import logging
import re
from typing import Any, Dict, List, Optional

from content_engine.models.templates import Template, TemplateVariable

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Template rendering engine"""
    
    def __init__(self):
        self._custom_filters = {}
        self._custom_functions = {}
    
    def add_filter(self, name: str, filter_func: callable) -> None:
        """Add a custom filter for template rendering"""
        self._custom_filters[name] = filter_func
    
    def add_function(self, name: str, func: callable) -> None:
        """Add a custom function for template rendering"""
        self._custom_functions[name] = func
    
    def render(
        self,
        template: Template,
        variables: Dict[str, Any],
    ) -> str:
        """Render a template with given variables"""
        # First, validate that all required variables are provided
        self._validate_variables(template, variables)
        
        # Start with the template content
        rendered = template.content
        
        # Apply variable substitution
        rendered = self._substitute_variables(rendered, template.variables, variables)
        
        # Apply custom filters if any
        rendered = self._apply_filters(rendered)
        
        # Apply custom functions if any
        rendered = self._apply_functions(rendered)
        
        return rendered
    
    def render_string(
        self,
        template_content: str,
        variables: Dict[str, Any],
        template_type: str = "text",
    ) -> str:
        """Render a template string with variables"""
        # Create a temporary template
        temp_template = Template(
            id="temp",
            name="temp",
            content=template_content,
            template_type=template_type,
        )
        
        return self.render(temp_template, variables)
    
    def _validate_variables(
        self,
        template: Template,
        variables: Dict[str, Any],
    ) -> None:
        """Validate that all required variables are provided"""
        for var in template.variables:
            if var.required and var.name not in variables:
                raise ValueError(f"Required variable '{var.name}' not provided")
    
    def _substitute_variables(
        self,
        content: str,
        template_vars: List[TemplateVariable],
        variables: Dict[str, Any],
    ) -> str:
        """Substitute variables in the template"""
        rendered = content
        
        # Sort variables by length (longest first) to avoid partial replacements
        sorted_vars = sorted(template_vars, key=lambda v: len(v.name), reverse=True)
        
        for var in sorted_vars:
            if var.name in variables:
                value = variables[var.name]
                placeholder = f"{{{{{var.name}}}}}"
                
                # Handle different types
                if isinstance(value, (list, tuple)):
                    replacement = ', '.join([str(item) for item in value])
                elif isinstance(value, dict):
                    replacement = str(value)
                else:
                    replacement = str(value)
                
                rendered = rendered.replace(placeholder, replacement)
            elif var.default_value is not None:
                # Use default value
                placeholder = f"{{{{{var.name}}}}}"
                rendered = rendered.replace(placeholder, str(var.default_value))
        
        return rendered
    
    def _apply_filters(self, content: str) -> str:
        """Apply custom filters to the content"""
        # Look for filter patterns like {{ variable | filter1 | filter2 }}
        pattern = r'\{\{\s*([^}]+)\s*\|\s*([^}]+)\s*\}\}'
        
        def replace_filter(match):
            var_name = match.group(1).strip()
            filter_chain = match.group(2).strip()
            
            # Get the variable value
            value = match.group(0)
            
            # For now, just return the original
            # In a full implementation, we would apply the filters
            return value
        
        return re.sub(pattern, replace_filter, content)
    
    def _apply_functions(self, content: str) -> str:
        """Apply custom functions to the content"""
        # Look for function patterns like {{ function_name(arg1, arg2) }}
        pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*\}\}'
        
        def replace_function(match):
            func_name = match.group(1)
            args_str = match.group(2)
            
            if func_name in self._custom_functions:
                try:
                    args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
                    result = self._custom_functions[func_name](*args)
                    return str(result)
                except Exception as e:
                    logger.error(f"Error applying function {func_name}: {e}")
                    return match.group(0)
            
            return match.group(0)
        
        return re.sub(pattern, replace_function, content)
    
    def render_markdown(
        self,
        template: Template,
        variables: Dict[str, Any],
    ) -> str:
        """Render a Markdown template"""
        rendered = self.render(template, variables)
        
        # Additional Markdown-specific processing
        # Ensure proper Markdown formatting
        rendered = self._format_markdown(rendered)
        
        return rendered
    
    def render_html(
        self,
        template: Template,
        variables: Dict[str, Any],
    ) -> str:
        """Render an HTML template"""
        rendered = self.render(template, variables)
        
        # Additional HTML-specific processing
        rendered = self._format_html(rendered)
        
        return rendered
    
    def _format_markdown(self, content: str) -> str:
        """Format Markdown content"""
        # Ensure proper spacing
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure headings have proper spacing
        content = re.sub(r'(^|\)#', r'\n\n#', content)
        content = re.sub(r'(^|\)##', r'\n\n##', content)
        content = re.sub(r'(^|\)###', r'\n\n###', content)
        
        return content.strip()
    
    def _format_html(self, content: str) -> str:
        """Format HTML content"""
        # Ensure proper HTML structure
        if not content.strip().startswith('<'):
            content = f"<p>{content}</p>"
        
        return content


# Default renderer instance
renderer = TemplateRenderer()
