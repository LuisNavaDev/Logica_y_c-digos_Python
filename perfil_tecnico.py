#creacion de un sistema para gestionar tecnicos, la salida final debe de ser perfil_tecnico

#Datos simples
id_empleado = 1233
nombre_completo = "Luis Angel Nava" 
estado = True
salario_hora = 255.50
salario_dia = salario_hora * 8 

#Datos compuestos
#Tupla (Datos que no se pueden modificar)
area_de_trabajo = ("Soporte", "Escritorio 3A")
#Lista
habilidades_unicas = ["Python","C++","Redes","Interconexiones","Python"]


#Diccionario de tickets_asignados
ticket1 = {
    "id_ticket": 2001,
    "problema": "La impresora no funciona",
    "prioridad": 2
}
ticket2 = {
    "id_ticket": 2002,
    "problema": "Area sin internet",
    "prioridad": 1 
}
ticket3 = {
    "id_ticket": 2003,
    "problema": "Sistema no responde",
    "prioridad": 1 
}

#Creacion del perfil completo
#Se deben de usar las variables que ya se definieron
perfil_tecnico = {
    "id_empleado": id_empleado,
    "nombre_completo": nombre_completo,
    "estado": estado,
    "salario_hora": salario_hora,
    "salario_dia": salario_dia,
    "area_de_trabajo": area_de_trabajo,
    "habilidades": set(habilidades_unicas),
    "tickets_asignados": [ticket1, ticket2, ticket3]
}


#Manipulacion de datos y acceso al Perfil

#Usamos comillas simples '' adentro para no chocar con las "" de la f string 

print(f"EL nombre del técnico es: {perfil_tecnico['nombre_completo']}")
print(f"El salario por hora es de: ${perfil_tecnico['salario_hora']}pesos mexicanos")
print(f"El salario por dia es de: ${perfil_tecnico['salario_dia']}pesos mexicanos")


#Se usan los adds para añadir datos 
perfil_tecnico['habilidades'].add("Linux")
print(f"Las habilidades del tecnico son: {perfil_tecnico['habilidades']}")

#Creacion del nuevo ticket 
nuevo_ticket ={
    "id_ticket": 2004,
    "problema": "Email no envia",
    "prioridad": 3
}

#Se añade el nuevo ticket con .append() a la lita dentro del perfil 
perfil_tecnico['tickets_asignados'].append(nuevo_ticket)

print("\n--- El perfil completo ya actualizado del tecnico es: ---")
print(perfil_tecnico)