#En este codigo, vamos a simular la evaluacion de un solicitante de prestamo
#basandonos en su perfil y el monto que desea


#Datos iniciales: Aqui viene el perdil del solicitante, estas variables se van a 
#usar para construir la logica del codigo 

perfil_solicitante = {
    "nombre": "Luis Angel Nava",
    "ingreso_mensual": 45000.0,
    "deudas_actuales": 15000.0,
    "score_credito": 750,
    "es_cliente_vip": False,
    "requisitos_faltantes": set()
}

monto_solcitado = 150000.0 

#Calculos aritmeticos, vamos a calcular el ratio de endeudamiento que tiene el cliente actualmente

ratio_actual = perfil_solicitante['deudas_actuales'] / perfil_solicitante['ingreso_mensual']
print(f"Evaluando a {perfil_solicitante['nombre']}")
print(f"Ratio de endeudamiento: {ratio_actual:.2f}")

#Flujo de desicion (uso de condicionales and, or, not)
#vamos a usar if, else, elif para la toma de decisiones 

#Bloque 1: Denegacion instantanea
if perfil_solicitante['requisitos_faltantes']:
    print("Faltan documentos, favor de completar expediente")
elif perfil_solicitante['score_credito'] > 750 or (perfil_solicitante['es_cliente_vip'] and perfil_solicitante['ingreso_mensual'] >= 40000.0):
        print("Cliente PREMIUM, tasa de interes baja")
elif perfil_solicitante['score_credito'] >=650 and ratio_actual < 0.35:
    print("Cliente ESTANDAR: Tasa de interes normal.")
else:
    print("SOLICITUD DENEGADA, CLIENTE NO APTO PARA PRESTAMO PERSONAL")


#Bloque 2, aprobacion premium
