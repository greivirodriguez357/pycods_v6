from fastapi import APIRouter

router = APIRouter()

# Tipos de paso: "aprender" (tarjeta de teoría), "opcion" (opción múltiple) y
# "ordenar" (ordena los bloques de código; se listan en el orden CORRECTO).
LESSONS = [
    {"exercise_id": 1, "titulo": "Variables y Mensajes", "pasos": [
        {"tipo": "aprender", "texto": "Una variable es como una caja con nombre. Dentro guardamos un dato. 📦",
         "codigo": 'nombre = "Ana"'},
        {"tipo": "opcion", "pregunta": "¿Qué hace esta línea?", "codigo": "edad = 9",
         "opciones": ["Guarda el número 9 en la caja edad", "Borra la edad", "Dibuja un nueve"],
         "correcta": 0, "pista": "El signo = guarda el dato dentro de la caja."},
        {"tipo": "ordenar", "instruccion": "Ordena el código para saludar a Ana.",
         "bloques": ['nombre = "Ana"', 'print("Hola", nombre)']},
        {"tipo": "opcion", "pregunta": "¿Cuál muestra un mensaje en la pantalla?",
         "opciones": ['print("Hola")', 'nombre = "Hola"', "if Hola"],
         "correcta": 0, "pista": "print significa mostrar."},
        {"tipo": "codigo", "instruccion": "Ahora escribe tú: muestra la variable nombre con print.",
         "inicial": 'nombre = "Ana"\n', "esperada": "Ana", "pista": "Escribe: print(nombre)"},
    ]},
    {"exercise_id": 2, "titulo": "Condicionales if", "pasos": [
        {"tipo": "aprender", "texto": "if es como hacer una pregunta: ¿está lloviendo? Si la respuesta es sí, llevo paraguas. ☔",
         "codigo": 'if lluvia:\n    print("Paraguas")'},
        {"tipo": "opcion", "pregunta": "Si hace sol, ¿qué se muestra?",
         "codigo": 'sol = True\nif sol:\n    print("Gafas")',
         "opciones": ["Gafas", "Nada", "Paraguas"], "correcta": 0,
         "pista": "sol es verdadero, así que se cumple el if."},
        {"tipo": "ordenar", "instruccion": "Ordena el código para decidir.",
         "bloques": ["edad = 9", "if edad >= 8:", '    print("Eres grande")']},
        {"tipo": "opcion", "pregunta": "¿Qué palabra usamos para decidir?",
         "opciones": ["if", "for", "print"], "correcta": 0, "pista": "if significa «si»."},
        {"tipo": "codigo", "instruccion": 'Escribe dentro del if: print("Grande")',
         "inicial": "edad = 9\nif edad >= 8:\n    ", "esperada": "Grande", "pista": 'Escribe: print("Grande") con comillas'},
    ]},
    {"exercise_id": 3, "titulo": "Bucles for", "pasos": [
        {"tipo": "aprender", "texto": "for repite una acción muchas veces, sin escribirla una y otra vez. 🔄",
         "codigo": 'for i in range(3):\n    print("Hola")'},
        {"tipo": "opcion", "pregunta": "¿Cuántas veces dice Hola?",
         "codigo": 'for i in range(3):\n    print("Hola")',
         "opciones": ["3 veces", "1 vez", "10 veces"], "correcta": 0, "pista": "range(3) cuenta 3 vueltas."},
        {"tipo": "ordenar", "instruccion": "Ordena el código para saltar 2 veces.",
         "bloques": ["for i in range(2):", '    print("Salto")']},
        {"tipo": "opcion", "pregunta": "¿Qué palabra repite acciones?",
         "opciones": ["for", "if", "nombre"], "correcta": 0, "pista": "for significa «para cada»."},
        {"tipo": "codigo", "instruccion": 'Escribe dentro del for: print("Hola")',
         "inicial": "for i in range(3):\n    ", "esperada": "Hola\nHola\nHola", "pista": 'Escribe: print("Hola") con comillas'},
    ]},
]

@router.get("/")
def get_lessons():
    return LESSONS
