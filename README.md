Proje ne yapıyor? (bir cümlede)

Ders slaytlarını (PDF) yükleyip doğal dilde soru sorabildiğin, cevabını slayt içeriğine dayandıran, gerektiğinde web'e çıkıp ek bilgi getirebilen ve hangi slayttan hangi bilgiyi aldığını gösterebilen bir soru-cevap sistemi.

Kullanıcı deneyimi nasıl olacak
Sen bir ders dosyasını (örneğin BBM416'nın bir haftalık slaytları) sisteme veriyorsun.
"Attention rollout ile GMAR arasındaki fark nedir?" gibi bir soru soruyorsun.
Sistem önce kendi slaytlarında arıyor, ilgili slaytları buluyor.
Eğer slaytlar yeterince açıklayıcı değilse (çoğu zaman değildir, slaytlar özettir), kendi kararıyla web'e çıkıp ek bağlam topluyor.
Sana bir cevap veriyor: "Slayt 14'e göre X... (ayrıca web'den: Y...)" gibi, kaynağını belli ederek.

Buradaki kritik nokta 4. adım — sistemin ne zaman web'e çıkacağına kendisinin karar vermesi. Bu yüzden buna "agent" diyoruz, düz bir soru-cevap botu demiyoruz.

Kullanacağımız kavramlar ve her birinin "neden"i

RAG (Retrieval-Augmented Generation)
LLM'lere sadece "bilgin var mı" diye soramayız çünkü (a) senin spesifik ders slaytların model eğitilirken hiç görülmemiştir, (b) LLM'ler bilmediği şeyi bile emin bir tavırla uydurabilir (hallucination). RAG'ın mantığı: soruyu sormadan önce, ilgili slaytları bir veritabanından çekip (retrieve) LLM'e "işte kaynak, buna dayanarak cevap ver" diye veriyoruz. Yani model hafızasından değil, gözünün önündeki gerçek metinden cevap üretiyor.

Embedding + Vector database
RAG'ın "ilgili slaytı bulma" kısmı nasıl çalışıyor? Metni sayısal bir vektöre çeviriyoruz (embedding) — anlamca yakın cümleler, vektör uzayında birbirine yakın noktalara düşüyor. Sorduğun soruyu da aynı şekilde vektöre çevirip, "bu vektöre en yakın slayt vektörleri hangileri" diye arıyoruz. Bunu hızlı yapabilmek için özel bir veritabanına (Qdrant gibi) ihtiyacımız var — normal bir SQL sorgusuyla "anlamca benzer" arama yapamazsın.

Chunking
Bir konuştuğumuz şeydi: slaytları embedding'e vermeden önce mantıklı parçalara bölmemiz gerekiyor (bizim durumumuzda doğal parça zaten "slayt"ın kendisi).

Agent (LangGraph ile)
Düz RAG şöyle çalışır: soru gelir → arama yapılır → cevap üretilir, tek adım. Ama biz istiyoruz ki sistem "bu soruyu cevaplamak için önce slaytlara bakayım, yetmezse web'e çıkayım, belki iki kaynağı birleştireyim" gibi çok adımlı bir karar süreci işletsin. Buna agent deniyor — LLM sadece metin üretmiyor, hangi aracı ne zaman kullanacağına da kendisi karar veriyor. LangGraph, bu çok adımlı karar sürecini yönetmemizi sağlayan bir kütüphane (bir "durum makinesi" / state machine gibi düşünebilirsin: agent bir durumdan diğerine geçiyor, her geçişte "şimdi ne yapmalıyım" diye karar veriyor).

Tool'lar
Agent'ın kullanabileceği somut yetenekler:

doc_search — slayt veritabanında arama yapar
web_search — internette arama yapar
İkisi de agent'a "fonksiyon" olarak tanımlanıyor; LLM hangisini çağıracağına, hangi parametrelerle çağıracağına kendisi karar veriyor (buna "function calling" deniyor).

Evaluation & guardrails
Sistemi kurduktan sonra "bu iyi çalışıyor mu" sorusunu insan gözüyle her seferinde kontrol edemeyiz. Otomatik metriklerle ölçeceğiz: cevap gerçekten slayta/kaynağa sadık mı (faithfulness), yoksa model bir şeyler mi uydurdu (hallucination)?

Serving (FastAPI + Docker)
Bütün bu mantığı bir web servisi haline getirip (/ask gibi bir endpoint), Docker ile paketleyeceğiz — geçen mesajda konuştuğumuz kısım.

Uçtan uca teknik akış
PDF slayt → (ingestion) → slayt slayt metin
   → (chunking) → embedding'e uygun parçalar
   → (embedding) → vektörler
   → (vector store) → Qdrant'a kaydet
   
Soru sorulunca:
soru → embedding → vector store'da benzer slaytları bul
   → agent (LangGraph): "yeterli mi? değilse web_search çağır"
   → LLM: kaynaklara dayanarak cevap üret
   → evaluation: cevap kaynağa sadık mı kontrol et
   → API üzerinden kullanıcıya dön