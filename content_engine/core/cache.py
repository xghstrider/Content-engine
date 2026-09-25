"""
Content caching implementation
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

import aiofiles

from content_engine.config.settings import get_settings

logger = logging.getLogger(__name__)


class ContentCache:
    """File-based content cache"""
    
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None):
        self.settings = get_settings()
        self.cache_dir = Path(cache_dir or self.settings.cache.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._memory_cache_timestamps: Dict[str, float] = {}
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a cached item"""
        if not self.settings.cache.cache_enabled:
            return None
        
        # Check memory cache first
        if key in self._memory_cache:
            if time.time() - self._memory_cache_timestamps[key] < self.settings.cache.cache_ttl:
                return self._memory_cache[key]
            else:
                del self._memory_cache[key]
                del self._memory_cache_timestamps[key]
        
        # Check file cache
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            try:
                async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    # Check TTL
                    if 'timestamp' in data:
                        if time.time() - data['timestamp'] > self.settings.cache.cache_ttl:
                            await cache_file.unlink()
                            return None
                    
                    # Add to memory cache
                    self._memory_cache[key] = data.get('data', {})
                    self._memory_cache_timestamps[key] = time.time()
                    
                    return data.get('data', {})
                    
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Cache read failed for {key}: {e}")
                return None
        
        return None
    
    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> None:
        """Set a cached item"""
        if not self.settings.cache.cache_enabled:
            return
        
        ttl = ttl or self.settings.cache.cache_ttl
        
        async with self._lock:
            # Add to memory cache
            self._memory_cache[key] = value
            self._memory_cache_timestamps[key] = time.time()
            
            # Write to file cache
            cache_file = self.cache_dir / f"{key}.json"
            
            try:
                data = {
                    'data': value,
                    'timestamp': time.time(),
                    'ttl': ttl,
                }
                
                async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=2))
                    
            except IOError as e:
                logger.warning(f"Cache write failed for {key}: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete a cached item"""
        async with self._lock:
            # Remove from memory cache
            if key in self._memory_cache:
                del self._memory_cache[key]
            if key in self._memory_cache_timestamps:
                del self._memory_cache_timestamps[key]
            
            # Remove from file cache
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                try:
                    await cache_file.unlink()
                    return True
                except IOError as e:
                    logger.warning(f"Cache delete failed for {key}: {e}")
                    return False
            
            return False
    
    async def clear(self) -> int:
        """Clear all cached items"""
        async with self._lock:
            count = 0
            
            # Clear memory cache
            self._memory_cache.clear()
            self._memory_cache_timestamps.clear()
            
            # Clear file cache
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    await cache_file.unlink()
                    count += 1
                except IOError as e:
                    logger.warning(f"Cache clear failed for {cache_file.name}: {e}")
            
            return count
    
    async def cleanup(self) -> int:
        """Cleanup expired cache items"""
        async with self._lock:
            count = 0
            current_time = time.time()
            
            # Cleanup memory cache
            expired_keys = [
                key for key, timestamp in self._memory_cache_timestamps.items()
                if current_time - timestamp > self.settings.cache.cache_ttl
            ]
            for key in expired_keys:
                del self._memory_cache[key]
                del self._memory_cache_timestamps[key]
                count += 1
            
            # Cleanup file cache
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        data = json.loads(content)
                        
                        if 'timestamp' in data:
                            if current_time - data['timestamp'] > data.get('ttl', self.settings.cache.cache_ttl):
                                await cache_file.unlink()
                                count += 1
                                
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Cache cleanup check failed for {cache_file.name}: {e}")
                    # Remove corrupted cache file
                    try:
                        await cache_file.unlink()
                        count += 1
                    except IOError:
                        pass
            
            return count
    
    async def size(self) -> int:
        """Get the number of cached items"""
        # Count memory cache
        count = len(self._memory_cache)
        
        # Count file cache
        count += len(list(self.cache_dir.glob("*.json")))
        
        return count
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        memory_size = len(self._memory_cache)
        file_size = len(list(self.cache_dir.glob("*.json")))
        
        total_size_bytes = 0
        for cache_file in self.cache_dir.glob("*.json"):
            total_size_bytes += cache_file.stat().st_size
        
        return {
            "memory_items": memory_size,
            "file_items": file_size,
            "total_items": memory_size + file_size,
            "total_size_bytes": total_size_bytes,
            "total_size_mb": total_size_bytes / (1024 * 1024),
            "cache_enabled": self.settings.cache.cache_enabled,
            "cache_ttl": self.settings.cache.cache_ttl,
            "max_cache_size": self.settings.cache.max_cache_size,
        }
