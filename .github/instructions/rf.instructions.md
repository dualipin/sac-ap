toma en cuenta que el sistema debe cumplir con lo siguiente

Requerimientos funcionales.
RF-01	Registro de ciudadano
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El sistema permitirá que un ciudadano cree una cuenta ingresando su CURP como identificador único, junto con información mínima personal y de contacto.
Precondición 	El ciudadano no debe tener una cuenta registrada previamente con la misma CURP.
Secuencia normal	Paso	Acción
	1	El ciudadano accede a la sección de registro.
	2	El ciudadano ingresa su CURP, nombre, apellido paterno, apellido materno y fecha de nacimiento.
	3	El sistema valida que la CURP tenga formato correcto y que no esté registrada.
	4	El ciudadano ingresa su correo electrónico, teléfono y contraseña.
	5	El ciudadano busca ingresa su código postal y selecciona la localidad donde vive, agrega la calle, numero exterior y opcionalmente el numero interior
	6	El sistema valida formatos y crea la cuenta.
	7	El sistema muestra un mensaje confirmando el registro exitoso.
Excepciones	2	Si la CURP no tiene formato válido, el sistema muestra un mensaje de error.
	3	Si la CURP ya está registrada, el sistema notifica y el caso de uso termina.
	4	Si el correo, teléfono o contraseña no tienen formato adecuado, se notifica al usuario.
	5	Si el código postal no existe se mostrará un mensaje de error, reintentar el paso hasta encontrar su localidad.
Postcondición	El ciudadano queda registrado y puede iniciar sesión.
Importancia	Alta
Frecuencia	1000 veces al día el primer mes, después 10 veces
Comentarios	Registro simplificado sin validaciones externas (RENAPO, Claves de verificación de contacto, domicilio).

RF-02	Autenticación
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El sistema permitirá que tanto ciudadanos como funcionarios inicien sesión en un único formulario. El ciudadano se autentica con CURP y contraseña; el funcionario con correo y contraseña.
Precondición 	Tener una cuenta registrada.
Secuencia normal	Paso	Acción
	1	El usuario accede a inicio de sesión.
	2	Ingresa sus credenciales (CURP o correo y contraseña).
	3	El sistema valida credenciales.
	4	El sistema identifica si la cuenta pertenece a ciudadano o funcionario.
	5	El sistema permite acceso y redirige al panel correspondiente según los permisos de usuario (Rol).
Excepciones	2	Formato invalido de credenciales.
	3	Credenciales incorrectas
Postcondición	El usuario accede al sistema y accede al panel correspondiente según su nivel de acceso.
Importancia	Alta
Frecuencia	1000 veces al día el primer mes, después 100 veces
Comentarios	Los ciudadanos y funcionarios compartirán el inicio de sesión.

RF-03	Cierre de sesión
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El sistema permitirá cerrar sesión invalidando el token (Código que identifica al usuario) o sesión activa.
Precondición 	El usuario debe haber iniciado sesión.
Secuencia normal	Paso	Acción
	1	El usuario elige “Cerrar sesión”.
	2	El sistema invalida sesión.
	3	Redirige a la pantalla inicial.
Excepciones	2	Sin sesión activa, el caso de uso termina.
Postcondición	El usuario queda sin autenticar.
Importancia	Alta
Frecuencia	1000 veces al día el primer mes, después 100 veces
Comentarios	Ninguno.

RF-04	Registro de solicitud
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El ciudadano podrá registrar una solicitud seleccionando categoría y proporcionando información básica.
Precondición 	El ciudadano debe estar autenticado (RF-02).
Secuencia normal	Paso	Acción
	1	Accede a “Nueva solicitud”.
	2	Selecciona categoría.
	3	Ingresa breve descripción.
	4	(Opcional) Adjunta archivo.
	5	El sistema genera folio y estado “Enviada”.
	6	Muestra confirmación.
Excepciones	2	No hay categorías disponibles.
	3	Descripción inválida.
	4	Archivo excede límite.
Postcondición	Solicitud registrada.
Importancia	Alta
Frecuencia	1000 veces al día el primer mes, después 100 veces
Comentarios	Ninguno.

RF-05	Consulta de solicitudes del ciudadano
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El sistema mostrará al ciudadano el listado de solicitudes que ha registrado.
Precondición 	El ciudadano debe estar autenticado (RF-02).
Secuencia normal	Paso	Acción
	1	Accede a “Mis solicitudes”.
	2	El sistema muestra folio, fecha, categoría, estado.
	3	El ciudadano puede ver detalles.
Excepciones	2	Sin solicitudes registradas.
Postcondición	Visualización de solicitudes.
Importancia	Alta
Frecuencia	1000 veces al día el primer mes, después 100 veces
Comentarios	Ninguno.

RF-06	Actualización de estado de solicitud (funcionario)
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El funcionario gestionará solicitudes de su dependencia, actualizando estado y añadiendo comentarios.
Precondición 	Funcionario autenticado y perteneciente a una dependencia.
Secuencia normal	Paso	Acción
	1	Funcionario accede a solicitudes de su dependencia.
	2	Selecciona una solicitud.
	3	Cambia el estado (En revisión / Resuelta).
	4	Agrega comentario o archivo.
	5	El sistema guarda cambios.
Excepciones	3	Estado inválido.
	4	Archivo excede límite.
Postcondición	Estado actualizado y visible para el ciudadano.
Importancia	Alta
Frecuencia	1000 veces al día el primer mes, después 100 veces
Comentarios	Ninguno.

RF-07	Consulta de solicitudes por funcionario
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El funcionario podrá consultar únicamente solicitudes pertenecientes a su dependencia.
Precondición 	El funcionario debe estar autenticado (RF-02).
Secuencia normal	Paso	Acción
	1	Accede al módulo administrativo.
	2	El sistema muestra solicitudes filtradas por su dependencia.
	3	Puede aplicar filtros simples por estado.
	4	Visualiza detalles.
Excepciones	2	Sin solicitudes disponibles.
Postcondición	Acceso a solicitudes restringido según dependencia.
Importancia	Alta
Frecuencia	1000 veces al día el primer mes, después 100 veces
Comentarios	Ninguno.

RF-08	Registro y gestión de funcionarios
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El sistema permitirá registrar funcionarios, asignarlos a una dependencia y definir su rol.
Precondición 	Usuario administrador autenticado.
Secuencia normal	Paso	Acción
	1	Admin accede a módulo de funcionarios.
	2	Ingresa nombre, correo, teléfono, dependencia y rol.
	3	El sistema valida y crea cuenta de funcionario.
	4	El funcionario puede iniciar sesión posteriormente.
Excepciones	3	Correo ya registrado.
	4	Dependencia inexistente.
Postcondición	Funcionario registrado con rol y dependencia.
Importancia	Alta
Frecuencia	5 veces al día el primer mes, después 1 veces
Comentarios	Ninguno.

RF-09	Gestión de programas de apoyo (funcionario)
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El sistema permitirá a funcionarios autorizados crear, editar y eliminar programas asociados a su dependencia.
Precondición 	El funcionario debe estar autenticado (RF-02).
Secuencia normal	Paso	Acción
	1	Accede al módulo de programas.
	2	Crea programa con título, descripción, requisitos y dependencia.
	3	Puede editar o eliminar programas existentes.
Excepciones	2	Datos incompletos.
	3	Intento de eliminar programa inexistente.
	3	Intento de modificar programa inexistente
Postcondición	Programa disponible para consulta ciudadana.
Importancia	Alta
Frecuencia	10 veces al día el primer mes, después 1 veces
Comentarios	Ninguno.

RF-10	Consulta de programas de apoyo (ciudadano)
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El ciudadano podrá ver todos los programas registrados.
Precondición 	El ciudadano debe estar autenticado (RF-02).
Secuencia normal	Paso	Acción
	1	Accede al módulo de programas.
	2	El sistema lista los programas.
	3	Puede ver detalles de uno.
Excepciones	2	Sin programas disponibles.
Postcondición	Información mostrada.
Importancia	Alta
Frecuencia	100 veces al día el primer mes, después 10 veces
Comentarios	Ninguno.

RF-11	Notificación de cambio de estado
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El sistema notificará al ciudadano cuando su solicitud cambie de estado.
Precondición 	Tener solicitudes registradas.
Secuencia normal	Paso	Acción
	1	El funcionario actualiza estado.
	2	El sistema registra cambio.
	3	Se genera notificación interna visible para el ciudadano.
Excepciones	2	Notificación fallida.
Postcondición	Ciudadano observa notificación.
Importancia	Alta
Frecuencia	1000 veces al día el primer mes, después 100 veces
Comentarios	Ninguno.

RF-12	Gestión de categorías de solicitud
Versión	1.0
Autores	Martin Sanchez Reyes
Descripción 	El sistema permitirá al usuario administrador crear, editar y deshabilitar las categorías de solicitud. Es fundamental que, al crear una categoría, esta se vincule obligatoriamente a una dependencia responsable.
Precondición 	•	Usuario administrador autenticado.
•	Deben existir dependencias registradas previamente en el sistema.

Secuencia normal	Paso	Acción
	1	El administrador accede al módulo de "Configuración de Categorías".
	2	Selecciona la opción "Nueva Categoría".
	3	Ingresa el nombre de la categoría 
	4	Ingresa una descripción o instrucciones para el ciudadano.
	5	Selecciona la dependencia responsable de un listado existente
	6	El sistema valida que el nombre no esté duplicado.
	7	El sistema guarda la categoría.
Excepciones	2	Nombre duplicado, el sistema notifica que ya existe una categoría con ese nombre.
	3	Falta asignar la dependencia o el nombre.
	4	Intento de eliminar una categoría que ya tiene solicitudes activas asociadas.
Postcondición	La categoría queda disponible inmediatamente en el listado de "Nueva Solicitud" (RF-04) para los ciudadanos y enrutará los reportes a la dependencia seleccionada.
Importancia	Alta
Frecuencia	10 veces al día el primer mes, después 2 veces
Comentarios	Es crítico que la asignación de dependencia sea obligatoria para evitar solicitudes huérfanas.

Requerimientos No Funcionales.
Tabla 1
Requerimiento No Funcional 01
RNF-01	Integridad de los datos
Tipo	Requisito no funcional
Prioridad	Alta
Descripción	La información almacenada en la base de datos debe mantenerse íntegra sin alteraciones no autorizadas.
Entrada	Datos ingresados por el usuario.
Proceso	El sistema valida y guarda datos sin permitir modificaciones ilegítimas.
Nota. Elaborador por el residente
Tabla 2
Requerimiento No Funcional 02
RNF-02	Disponibilidad del sistema
Tipo	Requisito no funcional
Prioridad	Alta
Descripción	El sistema debe estar disponible al menos el 95% del tiempo durante horas laborales del ayuntamiento.
Entrada	Solicitudes de acceso al sistema.
Proceso	El servidor responde.
Nota. Elaborado por el Residente.
Tabla 3
Requerimiento no Funcional
RNF-03	Seguridad de acceso
Tipo	Requisito no funcional
Prioridad	Alta
Descripción	El sistema debe restringir el acceso a módulos según el rol del usuario (ciudadano o funcionario).
Entrada	Intento de acceso.
Proceso	Validación de permisos según rol.
Nota. Elaborado por el residente.	
Tabla 4
Requerimiento no Funcional
RNF-04		Confidencialidad de la información
Tipo	Requisito no funcional
Prioridad	Alta
Descripción	La información sensible (datos personales y solicitudes) no debe estar disponible a usuarios no autorizados.
Entrada	Consultas a la plataforma.
Proceso	Responder solo datos permitidos según el rol y dependencia.
Tabla 5
Requerimiento no Funcional
RNF-05		Separación de datos por dependencia
Tipo	Requisito no funcional
Prioridad	Alta
Descripción	Los funcionarios solo podrán visualizar solicitudes relacionadas a su dependencia o coordinación.
Entrada	Consulta de solicitudes de funcionario.
Proceso	Filtrado automático por dependencia del usuario autenticado.
