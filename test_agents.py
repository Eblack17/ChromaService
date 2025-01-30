import asyncio
from app.agents.greeter import GreeterAgent
from app.agents.email_manager import EmailManagementAgent
from app.agents.content_manager import ContentManagementAgent
from app.agents.product_info import ProductInformationAgent

async def test_greeter_agent():
    print("\n=== Testing Greeter Agent ===")
    agent = GreeterAgent()
    
    # Test initial greeting
    response = await agent.process_message("Hi, I need help with ChromaPages")
    print("Initial Greeting Test:")
    print(f"User: Hi, I need help with ChromaPages")
    print(f"Agent: {response}")
    
    # Test routing capability
    message = "I want to optimize my ChromaPages website for better SEO"
    response = await agent.process_message(message)
    should_route = agent.should_route_to_specialist(message)
    print("\nRouting Test:")
    print(f"User: {message}")
    print(f"Agent: {response}")
    print(f"Should Route: {should_route}")

async def test_content_agent():
    print("\n=== Testing Content Management Agent ===")
    agent = ContentManagementAgent()
    
    # Test content optimization request
    message = "How can I improve my ChromaPages landing page to convert better?"
    response = await agent.process_message(message)
    print("Content Optimization Test:")
    print(f"User: {message}")
    print(f"Agent: {response}")
    
    # Test SEO recommendations
    content = """Welcome to ChromaPages - Your Ultimate Web Design Solution
    Create stunning websites with our intuitive drag-and-drop builder.
    Start your free trial today and bring your vision to life."""
    seo_recommendations = agent.get_seo_recommendations(content, "web design")
    print("\nSEO Recommendations Test:")
    print(f"Content: {content}")
    print(f"Recommendations: {seo_recommendations}")

async def test_email_agent():
    print("\n=== Testing Email Management Agent ===")
    agent = EmailManagementAgent()
    
    # Test email issue handling
    message = "I'm not receiving ChromaPages notification emails"
    response = await agent.process_message(message)
    category = agent.categorize_email_issue(message)
    print("Email Issue Test:")
    print(f"User: {message}")
    print(f"Agent: {response}")
    print(f"Category: {category}")

async def test_product_agent():
    print("\n=== Testing Product Information Agent ===")
    agent = ProductInformationAgent()
    
    # Test product inquiry
    message = "What features does ChromaPages offer for e-commerce websites?"
    response = await agent.process_message(message)
    query_type = agent.categorize_product_query(message)
    print("Product Information Test:")
    print(f"User: {message}")
    print(f"Agent: {response}")
    print(f"Query Type: {query_type}")

async def main():
    print("Starting ChromaPages Agent Tests...")
    
    try:
        # Test all agents
        await test_greeter_agent()
        await test_content_agent()
        await test_email_agent()
        await test_product_agent()
        
        print("\nAll agent tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 