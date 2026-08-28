from dotenv import load_dotenv
load_dotenv()
from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import retrieve, grade, web_search, generate



def route_after_grade(state: dict) -> str:
    if state["context_sufficient"]:
        return "generate"
    else:
        return "web_search"

def save_graph_image(path: str = "agent_graph.png"):
    graph_image = app.get_graph().draw_mermaid_png()
    with open(path, "wb") as f:
        f.write(graph_image)
    print(f"Grafik görseli kaydedildi: {path}")

graph = StateGraph(AgentState) #boş bir graph oluşturduk, AgentState'i verdik ve bu grafikte taşınacak veri şu şekilde oldu diyoruz.

"""
bir node ekliyoruz. İlk parametre, node'a grafikte vereceğimiz isim (string),
ikinci parametre ise gerçek fonksiyon. İsmi ayrı vermemizin sebebi: add_edge ve add_conditional_edges
içinde node'lara bu isimlerle referans vereceğiz, fonksiyonun kendisiyle değil.
"""
graph.add_node("retrieve", retrieve)
graph.add_node("grade", grade)
graph.add_node("web_search", web_search)
graph.add_node("generate", generate)

graph.set_entry_point("retrieve") # grafın başlayacağı node burası diye başlatıyoruz. 
# app.invoke çağırıldığında otomatik retrieve'den başlayacak

graph.add_edge("retrieve", "grade") # düz edge. retrieve'den sonra grade'e geç diyoruz.
graph.add_conditional_edges( #koşullu edge. grade ile başlıyor, route fonk sonucuna göre ilerliyor.
    "grade",
    route_after_grade,
    {
        "generate": "generate",
        "web_search": "web_search",
    }
)
graph.add_edge("web_search", "generate") # web search sonrası direkt generate'e git.
graph.add_edge("generate", END) # generate sonrası bitir.

app = graph.compile() # tüm node/edge tanımlarını bir app nesnesine döndürür. 


if __name__ == "__main__":
    save_graph_image()

    for question in ["What is lazy learning?", "What is the transformer attention mechanism?"]:
        result = app.invoke({"question": question})
        print(f"Soru: {question}")
        print(f"Yeterli mi: {result['context_sufficient']}")
        print(f"Cevap: {result['answer']}")
        print("=" * 50)