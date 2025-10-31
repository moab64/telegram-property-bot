import os
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class BotConfig:
    token: str
    admin_ids: List[int]

@dataclass
class DatabaseConfig:
    url: str

@dataclass
class CrawlerConfig:
    request_delay: int
    max_retries: int
    timeout: int
    user_agent: str

@dataclass
class CityConfig:
    divar: str
    sheypoor: str

@dataclass
class AppConfig:
    bot: BotConfig
    database: DatabaseConfig
    crawler: CrawlerConfig
    cities: Dict[str, CityConfig]
    property_types: Dict[str, str]

class ConfigLoader:
    def __init__(self):
        self.config_path = Path("config.yaml")
        self.env_file = Path(".env")
        self.config = None
    
    def load_config(self) -> AppConfig:
        """Load configuration from YAML file and environment variables"""
        try:
            # Load YAML config
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
            else:
                logger.warning("config.yaml not found, using default configuration")
                yaml_config = self._get_default_config()
            
            # Override with environment variables
            self._override_with_env(yaml_config)
            
            # Convert to dataclasses
            self.config = self._create_config_object(yaml_config)
            
            logger.info("Configuration loaded successfully")
            return self.config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Return default config as fallback
            return self._create_config_object(self._get_default_config())
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'bot': {
                'token': os.getenv('BOT_TOKEN', ''),
                'admin_ids': [int(x) for x in os.getenv('ADMIN_IDS', '63270167').split(',')]
            },
            'database': {
                'url': os.getenv('DATABASE_URL', 'sqlite:///property_bot.db')
            },
            'crawler': {
                'request_delay': 2,
                'max_retries': 3,
                'timeout': 30,
                'user_agent': 'PropertyBot/1.0'
            },
            'cities': {
                'sari': {
                    'divar': 'sari',
                    'sheypoor': 'sari'
                },
                'tehran': {
                    'divar': 'tehran',
                    'sheypoor': 'tehran'
                },
                'mashhad': {
                    'divar': 'mashhad',
                    'sheypoor': 'mashhad'
                }
            },
            'property_types': {
                'apartment': 'آپارتمان',
                'house': 'خانه و ویلا',
                'commercial': 'تجاری',
                'land': 'زمین',
                'garden': 'باغ'
            }
        }
    
    def _override_with_env(self, config: Dict[str, Any]):
        """Override configuration with environment variables"""
        # Bot token
        if os.getenv('BOT_TOKEN'):
            config['bot']['token'] = os.getenv('BOT_TOKEN')
        
        # Admin IDs
        if os.getenv('ADMIN_IDS'):
            admin_ids = [int(x.strip()) for x in os.getenv('ADMIN_IDS').split(',')]
            config['bot']['admin_ids'] = admin_ids
        
        # Database URL
        if os.getenv('DATABASE_URL'):
            config['database']['url'] = os.getenv('DATABASE_URL')
        
        # Crawler settings
        if os.getenv('CRAWLER_DELAY'):
            config['crawler']['request_delay'] = int(os.getenv('CRAWLER_DELAY'))
        if os.getenv('CRAWLER_RETRIES'):
            config['crawler']['max_retries'] = int(os.getenv('CRAWLER_RETRIES'))
        if os.getenv('CRAWLER_TIMEOUT'):
            config['crawler']['timeout'] = int(os.getenv('CRAWLER_TIMEOUT'))
    
    def _create_config_object(self, config_dict: Dict[str, Any]) -> AppConfig:
        """Convert dictionary to AppConfig object"""
        # Create nested objects
        bot_config = BotConfig(
            token=config_dict['bot']['token'],
            admin_ids=config_dict['bot']['admin_ids']
        )
        
        database_config = DatabaseConfig(
            url=config_dict['database']['url']
        )
        
        crawler_config = CrawlerConfig(
            request_delay=config_dict['crawler']['request_delay'],
            max_retries=config_dict['crawler']['max_retries'],
            timeout=config_dict['crawler']['timeout'],
            user_agent=config_dict['crawler']['user_agent']
        )
        
        # Create cities dictionary
        cities = {}
        for city_name, city_data in config_dict['cities'].items():
            cities[city_name] = CityConfig(
                divar=city_data['divar'],
                sheypoor=city_data['sheypoor']
            )
        
        property_types = config_dict.get('property_types', {})
        
        return AppConfig(
            bot=bot_config,
            database=database_config,
            crawler=crawler_config,
            cities=cities,
            property_types=property_types
        )
    
    def save_config(self, config: AppConfig):
        """Save configuration to YAML file"""
        try:
            config_dict = {
                'bot': {
                    'token': config.bot.token,
                    'admin_ids': config.bot.admin_ids
                },
                'database': {
                    'url': config.database.url
                },
                'crawler': {
                    'request_delay': config.crawler.request_delay,
                    'max_retries': config.crawler.max_retries,
                    'timeout': config.crawler.timeout,
                    'user_agent': config.crawler.user_agent
                },
                'cities': {
                    city_name: {
                        'divar': city_config.divar,
                        'sheypoor': city_config.sheypoor
                    }
                    for city_name, city_config in config.cities.items()
                },
                'property_types': config.property_types
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, allow_unicode=True, default_flow_style=False)
            
            logger.info("Configuration saved to config.yaml")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def create_env_example(self):
        """Create .env.example file"""
        env_example = """# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321

# Database Configuration
DATABASE_URL=sqlite:///property_bot.db
# For PostgreSQL: postgresql://username:password@localhost:5432/database_name

# Crawler Configuration (optional)
CRAWLER_DELAY=2
CRAWLER_RETRIES=3
CRAWLER_TIMEOUT=30

# Proxy Configuration (optional)
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=https://proxy.example.com:8080
"""
        
        with open('.env.example', 'w', encoding='utf-8') as f:
            f.write(env_example)
        
        logger.info(".env.example file created")

# Global config instance
_config_instance = None

def load_config() -> AppConfig:
    """Load configuration (singleton pattern)"""
    global _config_instance
    if _config_instance is None:
        loader = ConfigLoader()
        _config_instance = loader.load_config()
    return _config_instance

def get_city_slug(city_name: str, source: str) -> Optional[str]:
    """Get city slug for specific source"""
    config = load_config()
    city_config = config.cities.get(city_name)
    if city_config:
        return getattr(city_config, source, None)
    return None

def get_property_type_name(property_type: str) -> str:
    """Get localized property type name"""
    config = load_config()
    return config.property_types.get(property_type, property_type)

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    config = load_config()
    return user_id in config.bot.admin_ids

def get_crawler_headers() -> Dict[str, str]:
    """Get headers for crawler requests"""
    config = load_config()
    return {
        'User-Agent': config.crawler.user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }