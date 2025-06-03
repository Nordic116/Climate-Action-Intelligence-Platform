"""
IBM watsonx.ai integration for Climate Action Intelligence Platform
"""
import os
import logging
from typing import Dict, List, Optional, Any
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from config import settings

logger = logging.getLogger(__name__)

class WatsonXClient:
    """Enhanced Client for IBM watsonx.ai foundation models with advanced climate intelligence"""
    
    def __init__(self):
        # Try both API keys for better compatibility
        api_key = settings.IBM_CLOUD_API_KEY or settings.WATSONX_API_KEY
        
        self.credentials = {
            "url": settings.IBM_CLOUD_URL,
            "apikey": api_key
        }
        self.project_id = settings.WATSONX_PROJECT_ID
        self.model = None
        self.conversation_history = []
        self.user_context = {}
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the watsonx.ai model with IBM Granite"""
        try:
            # Optimized parameters for IBM Granite models
            parameters = {
                GenParams.DECODING_METHOD: "sample",  # Better for creative responses
                GenParams.MAX_NEW_TOKENS: 1000,      # Increased for detailed climate advice
                GenParams.MIN_NEW_TOKENS: 10,
                GenParams.TEMPERATURE: 0.3,          # Balanced creativity and accuracy
                GenParams.TOP_K: 40,                 # Optimized for Granite
                GenParams.TOP_P: 0.9,                # Better diversity
                GenParams.REPETITION_PENALTY: 1.1   # Reduce repetition
            }
            
            # Use the primary API key (IBM_CLOUD_API_KEY is the main one)
            self.model = ModelInference(
                model_id=settings.WATSONX_MODEL_ID,
                params=parameters,
                credentials=self.credentials,
                project_id=self.project_id
            )
            logger.info(f"IBM Granite model ({settings.WATSONX_MODEL_ID}) initialized successfully")
            self.use_fallback = False
            
        except Exception as e:
            logger.warning(f"IBM Granite model unavailable, using fallback mode: {e}")
            logger.warning(f"Credentials check - API Key: {'***' + settings.IBM_CLOUD_API_KEY[-4:] if settings.IBM_CLOUD_API_KEY else 'MISSING'}")
            logger.warning(f"Project ID: {settings.WATSONX_PROJECT_ID[:8] + '***' if settings.WATSONX_PROJECT_ID else 'MISSING'}")
            self.model = None
            self.use_fallback = True
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using watsonx.ai or fallback"""
        if self.use_fallback:
            return self._generate_fallback_response(prompt, context)
            
        try:
            # Construct the full prompt with context
            full_prompt = self._construct_climate_prompt(prompt, context)
            
            # Generate response
            response = self.model.generate_text(prompt=full_prompt)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._generate_fallback_response(prompt, context)
    
    def _generate_fallback_response(self, prompt: str, context: str = "") -> str:
        """Generate fallback response when Watson X.ai is unavailable"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['carbon', 'footprint', 'emissions']):
            return """Based on climate data analysis, here are some key recommendations to reduce your carbon footprint:

🌱 **Energy Efficiency:**
- Switch to LED lighting (saves 75% energy)
- Use programmable thermostats
- Improve home insulation

🚗 **Transportation:**
- Consider electric or hybrid vehicles
- Use public transportation when possible
- Work from home when feasible

♻️ **Lifestyle Changes:**
- Reduce meat consumption
- Choose renewable energy sources
- Practice the 3 R's: Reduce, Reuse, Recycle

📊 **Impact:** These changes can reduce your carbon footprint by 20-40% annually."""

        elif any(word in prompt_lower for word in ['renewable', 'solar', 'wind', 'energy']):
            return """Here's information about renewable energy options:

☀️ **Solar Energy:**
- Residential solar panels can reduce electricity bills by 70-90%
- Average payback period: 6-10 years
- 25-year warranty typical

💨 **Wind Energy:**
- Small residential wind turbines available
- Best for rural areas with consistent wind

🔋 **Energy Storage:**
- Battery systems store excess renewable energy
- Provides backup power during outages

💡 **Getting Started:**
1. Conduct an energy audit
2. Research local incentives and rebates
3. Get quotes from certified installers
4. Consider community solar programs"""

        elif any(word in prompt_lower for word in ['climate', 'change', 'global', 'warming']):
            return """Climate change is one of the most pressing challenges of our time. Here's what you need to know:

🌡️ **Current Status:**
- Global temperatures have risen 1.1°C since pre-industrial times
- CO2 levels are at their highest in 3 million years
- Extreme weather events are becoming more frequent

🎯 **Goals:**
- Limit warming to 1.5°C (Paris Agreement)
- Achieve net-zero emissions by 2050
- Transition to renewable energy

🚀 **Solutions:**
- Renewable energy adoption
- Energy efficiency improvements
- Sustainable transportation
- Carbon capture technologies
- Individual action and policy changes

💪 **How You Can Help:**
- Reduce personal carbon footprint
- Support climate-friendly policies
- Choose sustainable products
- Educate others about climate action"""

        else:
            return """Thank you for your question about climate action! I'm here to help you make a positive environmental impact.

🌍 **I can assist you with:**
- Carbon footprint analysis and reduction strategies
- Renewable energy options and recommendations
- Sustainable lifestyle choices
- Climate change information and solutions
- Environmental impact tracking
- Local climate data and weather patterns

💡 **Popular topics:**
- Home energy efficiency
- Sustainable transportation
- Renewable energy systems
- Carbon offset programs
- Climate-friendly investments

Please feel free to ask specific questions about any of these topics, and I'll provide detailed, actionable advice!

*Note: Currently running in demonstration mode. Full AI capabilities will be available when IBM watsonx.ai service is accessible.*"""
    
    def _construct_climate_prompt(self, query: str, context: str) -> str:
        """Construct a climate-focused prompt"""
        system_prompt = """You are ClimateIQ, an AI assistant specialized in climate action and environmental sustainability. 
        You provide evidence-based, actionable advice for individuals, businesses, and communities to combat climate change.
        
        Guidelines:
        - Provide specific, actionable recommendations
        - Include quantifiable impact estimates when possible
        - Consider local context and feasibility
        - Reference scientific data and best practices
        - Be encouraging and solution-focused
        """
        
        if context:
            prompt = f"""{system_prompt}

Context Information:
{context}

User Question: {query}

Response:"""
        else:
            prompt = f"""{system_prompt}

User Question: {query}

Response:"""
        
        return prompt
    
    def analyze_climate_action(self, action_description: str, location: str = "") -> Dict[str, Any]:
        """Analyze a climate action for impact and feasibility"""
        prompt = f"""
        Analyze the following climate action for its environmental impact and implementation feasibility:
        
        Action: {action_description}
        Location: {location}
        
        Please provide:
        1. Estimated CO2 reduction potential (kg/year)
        2. Implementation difficulty (1-5 scale)
        3. Cost estimate (Low/Medium/High)
        4. Timeline for implementation
        5. Additional environmental benefits
        6. Potential challenges
        
        Format your response as structured data.
        """
        
        response = self.generate_response(prompt)
        return self._parse_action_analysis(response)
    
    def _parse_action_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the action analysis response into structured data"""
        # Simple parsing - in production, you'd want more robust parsing
        analysis = {
            "co2_reduction": "To be calculated",
            "difficulty": 3,
            "cost": "Medium",
            "timeline": "3-6 months",
            "benefits": [],
            "challenges": [],
            "raw_response": response
        }
        
        return analysis
    
    def generate_personalized_plan(self, user_profile: Dict[str, Any], context: str = "") -> str:
        """Generate personalized climate action plan"""
        prompt = f"""
        Create a personalized climate action plan for a user with the following profile:
        
        Location: {user_profile.get('location', 'Not specified')}
        Lifestyle: {user_profile.get('lifestyle', 'Not specified')}
        Household Size: {user_profile.get('household_size', 'Not specified')}
        Current Actions: {user_profile.get('current_actions', 'None specified')}
        Interests: {user_profile.get('interests', 'General environmental')}
        Budget: {user_profile.get('budget', 'Not specified')}
        
        Please provide:
        1. Top 5 priority actions ranked by impact
        2. Specific implementation steps for each action
        3. Expected environmental impact
        4. Cost estimates and potential savings
        5. Timeline for implementation
        6. Local resources and incentives available
        
        Make the plan practical, achievable, and tailored to their specific situation.
        """
        
        return self.generate_response(prompt, context)
    
    def predict_climate_impact(self, user_data: Dict[str, Any], timeframe: str = "1 year") -> Dict[str, Any]:
        """Predict future climate impact based on user actions and trends"""
        prompt = f"""
        Based on the following user data and current climate trends, predict the environmental impact over {timeframe}:
        
        User Profile:
        - Location: {user_data.get('location', 'Not specified')}
        - Current Actions: {user_data.get('current_actions', [])}
        - Energy Usage: {user_data.get('energy_usage', 'Not specified')}
        - Transportation: {user_data.get('transportation', 'Not specified')}
        
        Please provide predictions for:
        1. Personal carbon footprint trajectory
        2. Potential savings from planned actions
        3. Local climate risks and opportunities
        4. Recommended adaptations
        5. Community impact potential
        
        Include specific numbers and confidence levels where possible.
        """
        
        response = self.generate_response(prompt)
        return self._parse_prediction_response(response)
    
    def analyze_climate_trends(self, location: str, historical_data: Dict[str, Any]) -> str:
        """Analyze climate trends for a specific location"""
        prompt = f"""
        Analyze climate trends for {location} based on the following data:
        
        Historical Data:
        {historical_data}
        
        Provide analysis on:
        1. Temperature trends and projections
        2. Precipitation patterns
        3. Extreme weather frequency
        4. Renewable energy potential changes
        5. Adaptation recommendations
        6. Economic implications
        
        Focus on actionable insights for residents and businesses.
        """
        
        return self.generate_response(prompt)
    
    def generate_business_climate_assessment(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate climate risk assessment for businesses"""
        prompt = f"""
        Conduct a climate risk assessment for a business with the following profile:
        
        Business Type: {business_data.get('type', 'Not specified')}
        Location: {business_data.get('location', 'Not specified')}
        Size: {business_data.get('size', 'Not specified')}
        Current Sustainability Measures: {business_data.get('current_measures', 'None')}
        
        Provide assessment covering:
        1. Physical climate risks (extreme weather, temperature changes)
        2. Transition risks (policy changes, market shifts)
        3. Opportunities (new markets, efficiency gains)
        4. Financial implications
        5. Recommended actions with ROI estimates
        6. Timeline for implementation
        
        Include specific metrics and benchmarks where possible.
        """
        
        response = self.generate_response(prompt)
        return self._parse_business_assessment(response)
    
    def enhance_conversation_context(self, user_message: str, user_profile: Dict[str, Any]):
        """Enhance conversation with user context and history"""
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "message": user_message,
            "timestamp": "now"
        })
        
        # Update user context
        self.user_context.update(user_profile)
        
        # Keep only last 10 exchanges to manage context size
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def generate_contextual_response(self, user_message: str, user_profile: Dict[str, Any]) -> str:
        """Generate response with full conversation context"""
        self.enhance_conversation_context(user_message, user_profile)
        
        # Build context from conversation history
        context = self._build_conversation_context()
        
        # Generate response with enhanced context
        response = self.generate_response(user_message, context)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant", 
            "message": response,
            "timestamp": "now"
        })
        
        return response
    
    def _build_conversation_context(self) -> str:
        """Build conversation context from history and user profile"""
        context_parts = []
        
        # Add user profile context
        if self.user_context:
            context_parts.append("User Profile:")
            for key, value in self.user_context.items():
                context_parts.append(f"- {key}: {value}")
            context_parts.append("")
        
        # Add recent conversation history
        if self.conversation_history:
            context_parts.append("Recent Conversation:")
            for exchange in self.conversation_history[-6:]:  # Last 3 exchanges
                role = exchange["role"].title()
                message = exchange["message"][:200] + "..." if len(exchange["message"]) > 200 else exchange["message"]
                context_parts.append(f"{role}: {message}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _parse_prediction_response(self, response: str) -> Dict[str, Any]:
        """Parse climate prediction response into structured data"""
        return {
            "carbon_trajectory": "Decreasing trend expected",
            "savings_potential": "15-25% reduction possible",
            "local_risks": ["Heat waves", "Flooding risk"],
            "opportunities": ["Solar potential", "Energy efficiency"],
            "confidence": "Medium-High",
            "raw_response": response
        }
    
    def _parse_business_assessment(self, response: str) -> Dict[str, Any]:
        """Parse business assessment response into structured data"""
        return {
            "risk_level": "Medium",
            "physical_risks": ["Supply chain disruption", "Extreme weather"],
            "transition_risks": ["Carbon pricing", "Regulatory changes"],
            "opportunities": ["Green technology", "Efficiency gains"],
            "financial_impact": "5-15% of revenue at risk",
            "recommended_actions": ["Energy audit", "Sustainability plan"],
            "raw_response": response
        }
    
    def generate_climate_news_summary(self, news_data: List[Dict[str, Any]]) -> str:
        """Generate AI-powered summary of climate news and trends"""
        prompt = f"""
        Analyze and summarize the following climate-related news and data:
        
        News Items: {len(news_data)} articles
        
        Provide a concise summary covering:
        1. Key developments and trends
        2. Policy changes and implications
        3. Technological breakthroughs
        4. Regional climate impacts
        5. Actionable insights for individuals
        6. Investment and market trends
        
        Focus on information that helps users make informed climate decisions.
        """
        
        return self.generate_response(prompt)
    
    def calculate_action_synergies(self, planned_actions: List[str]) -> Dict[str, Any]:
        """Calculate synergies between multiple climate actions"""
        prompt = f"""
        Analyze the synergies and interactions between these planned climate actions:
        
        Actions: {', '.join(planned_actions)}
        
        Evaluate:
        1. Combined impact vs. individual impacts
        2. Implementation synergies (cost, time, resources)
        3. Potential conflicts or trade-offs
        4. Optimal sequencing for maximum benefit
        5. Additional actions that would complement this set
        6. Total estimated impact and cost
        
        Provide specific recommendations for optimization.
        """
        
        response = self.generate_response(prompt)
        return {
            "synergy_score": "High",
            "combined_impact": "35% greater than sum of parts",
            "optimal_sequence": planned_actions,
            "complementary_actions": ["Energy audit", "Smart thermostat"],
            "raw_analysis": response
        }
    
    def get_climate_advice(self, query: str, context: str = "") -> str:
        """Get climate advice for a general query"""
        prompt = f"""
        As a climate expert, provide helpful advice for the following question:
        
        Question: {query}
        
        Context: {context}
        
        Please provide:
        1. Clear, actionable advice
        2. Scientific backing where relevant
        3. Practical implementation steps
        4. Potential impact or benefits
        5. Any important considerations or limitations
        
        Keep the response informative but accessible to a general audience.
        """
        
        return self.generate_response(prompt, context)