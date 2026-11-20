# Diseño del agente y estrategia de prompts (Parte A)

## 1. Tema y público
- **Tema:** Cloud Computing, enfocado en la certificación **AWS Certified Cloud Practitioner (CLF-C02)**.
- **Público:** estudiantes sin experiencia profunda en AWS que preparan el examen.
- **Nombre del asistente:** CloudCoach.

## 2. Arquitectura del prompt

```
System prompt final = BASE_PROMPT  +  instrucciones del PERFIL elegido
Mensajes enviados   = [System prompt] + últimos N mensajes del historial + pregunta nueva
```

| Capa | Qué fija | Dónde está |
|---|---|---|
| Prompt base | Rol general, dominios del CLF-C02 con su peso, idioma, límites, formato | `src/prompts.py` → `BASE_PROMPT` |
| Perfil | Forma de responder (tutor, examinador, arquitecto) | `src/prompts.py` → `PROFILES` |
| Historial | Contexto de la conversación | `st.session_state.messages` |

## 3. Técnicas usadas y por qué
1. **Role prompting** ("Eres CloudCoach..."): orienta el vocabulario y el tono.
2. **Delimitación del dominio**: listar los 4 dominios del examen con su peso le da al modelo un "mapa" de qué es relevante y evita respuestas genéricas.
3. **Guardrails en lenguaje natural**: no salirse del tema, no inventar datos, recomendar documentación oficial cuando dude (reduce alucinaciones).
4. **Instrucciones de formato**: párrafos cortos y Markdown, porque Streamlit renderiza Markdown.
5. **Perfiles intercambiables**: el mismo modelo adopta roles distintos solo cambiando una parte del system prompt (requisito de "distintos perfiles de expertos").
6. **Temperatura baja (0.3)**: respuestas más consistentes y factuales, adecuadas para estudio.

## 4. Perfiles
| Perfil | Objetivo | Comportamiento clave |
|---|---|---|
| 🎓 Tutor | Entender conceptos | Analogía + "Para el examen recuerda" + pregunta de verificación |
| 📝 Examinador | Practicar | Una pregunta tipo examen, no revela la respuesta hasta que el usuario conteste |
| 🏗️ Arquitecto | Aplicar a casos reales | Caso de negocio → servicios → pilar Well-Architected |

## 5. Casos de prueba (Parte C)
| # | Perfil | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Tutor | ¿Qué es una zona de disponibilidad? | Explicación + analogía + puntos para el examen |
| 2 | Examinador | Hazme una pregunta sobre IAM | Pregunta A-D sin la respuesta |
| 3 | Examinador | (responder "B") | Corrige y explica cada opción |
| 4 | Arquitecto | Una tienda en línea quiere escalar en Black Friday | Auto Scaling, ELB, CloudFront… + pilar |
| 5 | Cualquiera | ¿Quién ganó el mundial? | Rechaza con amabilidad y reconduce |
| 6 | Cualquiera | "Me llamo Ana" y luego "¿cómo me llamo?" | Recuerda el nombre (historial) |
| 7 | Cualquiera | ¿Cuánto cuesta exactamente un t3.micro hoy? | Aclara que verifique en la calculadora oficial |
