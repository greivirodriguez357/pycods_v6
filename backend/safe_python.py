"""
Mini-intérprete SEGURO de Python para niños.
No usa exec/eval: recorre el árbol sintáctico (ast) y solo entiende lo que enseña Pycods:
variables, print(), operaciones, if/elif/else, for sobre range/listas/texto, while, listas y f-strings.
Sin imports, sin archivos, sin red, con límite de pasos y de salida.
"""
import ast
import operator

MAX_STEPS = 20000
MAX_OUTPUT = 2000
MAX_CODE = 1500
MAX_SEQ = 1000

class PyError(Exception):
    pass

BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
          ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod}
CMPOPS = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le,
          ast.Gt: operator.gt, ast.GtE: operator.ge,
          ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b}
FUNCS = {"range": range, "len": len, "str": str, "int": int, "float": float, "abs": abs, "min": min, "max": max}
METHODS = {"upper", "lower", "title", "strip", "append"}
NEW = "Todavía no usamos eso en Pycods 🌱"

class Runner:
    def __init__(self):
        self.vars = {}
        self.out = []
        self.size = 0
        self.steps = 0

    def tick(self):
        self.steps += 1
        if self.steps > MAX_STEPS:
            raise PyError("Tu programa se repite demasiado. ¿Falta parar el bucle? 🔄")

    # ---------- sentencias ----------
    def run(self, code):
        if len(code) > MAX_CODE:
            raise PyError("El código es muy largo. ¡Prueba con algo más cortito! ✂️")
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise PyError(f"Hay un error de escritura en la línea {e.lineno}. Revisa las comillas, los paréntesis y los dos puntos ( : ) ✏️")
        except Exception:
            raise PyError("No pude leer tu código. Revisa que esté bien escrito ✏️")
        self.block(tree.body)
        return "\n".join(self.out)

    def block(self, body):
        for st in body:
            self.exec(st)

    def exec(self, n):
        self.tick()
        if isinstance(n, ast.Assign):
            if len(n.targets) != 1 or not isinstance(n.targets[0], ast.Name):
                raise PyError(NEW)
            self.vars[n.targets[0].id] = self.ev(n.value)
        elif isinstance(n, ast.AugAssign):
            if not isinstance(n.target, ast.Name) or type(n.op) not in BINOPS:
                raise PyError(NEW)
            self.vars[n.target.id] = self.binop(n.op, self.get(n.target.id), self.ev(n.value))
        elif isinstance(n, ast.Expr):
            v = n.value
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "print":
                self.do_print(v)
            elif isinstance(v, ast.Constant):
                pass
            else:
                self.ev(v)
        elif isinstance(n, ast.If):
            self.block(n.body if self.ev(n.test) else n.orelse)
        elif isinstance(n, ast.For):
            if not isinstance(n.target, ast.Name) or n.orelse:
                raise PyError(NEW)
            seq = self.ev(n.iter)
            if not isinstance(seq, (range, list, str)):
                raise PyError("El for necesita algo para recorrer, como range(3) o una lista 🔁")
            for item in seq:
                self.tick()
                self.vars[n.target.id] = item
                self.block(n.body)
        elif isinstance(n, ast.While):
            if n.orelse:
                raise PyError(NEW)
            while self.ev(n.test):
                self.tick()
                self.block(n.body)
        elif isinstance(n, ast.Pass):
            pass
        else:
            raise PyError(NEW)

    def do_print(self, call):
        args = [self.ev(a) for a in call.args]
        sep, end = " ", "\n"
        for kw in call.keywords:
            if kw.arg == "sep":
                sep = str(self.ev(kw.value))
            elif kw.arg == "end":
                end = str(self.ev(kw.value))
            else:
                raise PyError(NEW)
        text = sep.join(str(a) for a in args) + end
        self.size += len(text)
        if self.size > MAX_OUTPUT:
            raise PyError("Tu programa muestra demasiado texto. ¡Prueba con menos! 📜")
        self.out.append(text[:-1] if text.endswith("\n") and end == "\n" else text)

    # ---------- expresiones ----------
    def get(self, name):
        if name not in self.vars:
            raise PyError(f"La variable '{name}' todavía no existe. ¿La escribiste igual que antes? 🔍")
        return self.vars[name]

    def binop(self, op, a, b):
        try:
            res = BINOPS[type(op)](a, b)
        except ZeroDivisionError:
            raise PyError("No se puede dividir entre cero 🚫")
        except TypeError:
            raise PyError("No puedes mezclar texto y números así. Prueba con str() para convertir 🔤")
        if isinstance(res, (str, list)) and len(res) > MAX_SEQ:
            raise PyError("El resultado es demasiado grande. ¡Prueba con números más chicos! 📏")
        return res

    def ev(self, n):
        self.tick()
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (str, int, float, bool)) or n.value is None:
                return n.value
            raise PyError(NEW)
        if isinstance(n, ast.Name):
            return self.get(n.id)
        if isinstance(n, ast.BinOp) and type(n.op) in BINOPS:
            return self.binop(n.op, self.ev(n.left), self.ev(n.right))
        if isinstance(n, ast.UnaryOp):
            v = self.ev(n.operand)
            if isinstance(n.op, ast.USub): return -v
            if isinstance(n.op, ast.Not): return not v
            raise PyError(NEW)
        if isinstance(n, ast.BoolOp):
            if isinstance(n.op, ast.And):
                r = True
                for v in n.values:
                    r = self.ev(v)
                    if not r: return r
                return r
            r = False
            for v in n.values:
                r = self.ev(v)
                if r: return r
            return r
        if isinstance(n, ast.Compare):
            left = self.ev(n.left)
            for op, comp in zip(n.ops, n.comparators):
                if type(op) not in CMPOPS:
                    raise PyError(NEW)
                right = self.ev(comp)
                try:
                    ok = CMPOPS[type(op)](left, right)
                except TypeError:
                    raise PyError("No puedo comparar cosas de tipos distintos, como un texto con un número ⚖️")
                if not ok: return False
                left = right
            return True
        if isinstance(n, (ast.List, ast.Tuple)):
            return [self.ev(e) for e in n.elts]
        if isinstance(n, ast.Subscript) and not isinstance(n.slice, ast.Slice):
            seq, idx = self.ev(n.value), self.ev(n.slice)
            try:
                return seq[idx]
            except (IndexError, TypeError, KeyError):
                raise PyError("Esa posición no existe en la lista. Recuerda que se empieza a contar desde 0 🔢")
        if isinstance(n, ast.JoinedStr):
            parts = []
            for p in n.values:
                if isinstance(p, ast.Constant): parts.append(str(p.value))
                elif isinstance(p, ast.FormattedValue) and p.format_spec is None: parts.append(str(self.ev(p.value)))
                else: raise PyError(NEW)
            return "".join(parts)
        if isinstance(n, ast.Call):
            return self.call(n)
        raise PyError(NEW)

    def call(self, n):
        if isinstance(n.func, ast.Name):
            fn = FUNCS.get(n.func.id)
            if fn is None:
                if n.func.id == "print":
                    raise PyError("print() va solito en una línea, sin guardarlo en una variable 💬")
                raise PyError(NEW)
            args = [self.ev(a) for a in n.args]
            if n.keywords:
                raise PyError(NEW)
            try:
                if fn is range and any(abs(a) > MAX_STEPS for a in args if isinstance(a, int)):
                    raise PyError("Ese range es demasiado grande. ¡Prueba con uno más chico! 📏")
                return fn(*args)
            except PyError:
                raise
            except (TypeError, ValueError):
                raise PyError(f"No pude usar {n.func.id}() con esos datos 🤔")
        if isinstance(n.func, ast.Attribute) and n.func.attr in METHODS:
            obj, args = self.ev(n.func.value), [self.ev(a) for a in n.args]
            try:
                return getattr(obj, n.func.attr)(*args)
            except (TypeError, AttributeError):
                raise PyError(f"No pude usar .{n.func.attr}() ahí 🤔")
        raise PyError(NEW)


def run_code(code: str):
    """Ejecuta código de forma segura. Devuelve {'salida': str, 'error': str|None}."""
    r = Runner()
    try:
        out = r.run(code)
        return {"salida": out, "error": None}
    except PyError as e:
        return {"salida": "\n".join(r.out), "error": str(e)}
    except RecursionError:
        return {"salida": "", "error": "Tu código es demasiado enredado. ¡Prueba con algo más sencillo! 🧶"}
    except Exception:
        return {"salida": "", "error": "Algo salió mal con tu código. Revísalo con calma 🔍"}
