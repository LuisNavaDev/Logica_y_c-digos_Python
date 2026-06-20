#EN ESTE CODIGO VAMOS A HACER UN SIMULADOR REAL PARA DAR LOGICA DE INSCRIPCION DE UN ESTUDIANTE A UN CURSO 
#VAMOS A EMPLEAR DICCIONARIOS Y LISTAS, OPERADORES ARTIMETICOS, COMPARACIONES Y CONDICIONALES 
#LA SITUACION ES LA SIGUIENTE
#Tienes un estudiante que quiere entrar al curso de "Python Master". 
#Tú eres el "portero" digital. Tu código debe decidir si entra o no, y si entra, actualizar toda la base de datos.


#DATOS INICIALES
estudiante =  {
    "nombre": "Luis Angel Nava",
    "edad": 26,
    "presupuesto": 2500.0, 
    "esta_bloqueado": False, 
    "cursos_inscritos": {"HTML", "CSS", "JAVASCRIPT"}
}

curso = {
    "nombre": "Python Master",
    "precio_base": 2000.0, 
    "cupos_disponibles": 1, 
    "alumnos_lista": ["Juan Hernandez", "Monica Gonzalez", "Miriam Valdez", "Regina Montes", "Angel Fernandez"]
    
}

#VARIABLES DE PRESUPUESTO

impuesto = curso['precio_base'] * 0.16
precio_final = curso['precio_base'] + impuesto
cantidad = precio_final - estudiante['presupuesto']

#VALIDACIONES Y LOGICA 

if estudiante['esta_bloqueado']:
    print("ACCESO DENEGADO: USUARIO BLOQUEADO")
    
elif curso['cupos_disponibles'] != 0:
    print("CUPOS DISPONIBLES... VERIFICANDO FONDOS")
    if estudiante['presupuesto'] >= precio_final:
        print("BIENVENIDO A TU NUEVO CURSO")
        
        estudiante['presupuesto'] -= precio_final
        curso['cupos_disponibles'] -= 1 
        curso['alumnos_lista'].append(estudiante['nombre'])
        estudiante['cursos_inscritos'].add(curso['nombre'])
        print(f"¡INSCRIPCION EXITOSA! Bienvenido {estudiante['nombre']} a: {curso['nombre']}. Nuevo saldo: $ {estudiante['presupuesto']}")

    
    else:
        print(f"FONDOS INSUFICIENTES, TE FALTAN ${cantidad}")
else:
    print("LO SENTIMOS CURSO LLENO")
    
print(estudiante)