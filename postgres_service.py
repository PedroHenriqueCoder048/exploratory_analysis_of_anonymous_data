import psycopg2

class PostgresDB:
	"""
	Pequena classe para gerenciar conexão e operações simples.
	Altere os params de conexão conforme necessário.
	"""
	def __init__(self, host, port, dbname, user, password):
		self.params = {
			"host": host,
			"port": port,
			"dbname": dbname,
			"user": user,
			"password": password
		}
		self.conn = None

	def connect(self):
		if self.conn is None or self.conn.closed:
			self.conn = psycopg2.connect(**self.params)

	def close(self):
		"""Fecha a conexão de forma segura e garante que self.conn seja limpo."""
		if getattr(self, "conn", None) is None:
			return
		try:
			# tentar desfazer transações pendentes para evitar locks
			try:
				if not self.conn.closed:
					self.conn.rollback()
			except Exception:
				# ignorar erros de rollback
				pass

			# tentar fechar a conexão se ainda estiver aberta
			try:
				if not self.conn.closed:
					self.conn.close()
			except Exception:
				# ignorar erros ao fechar
				pass
		finally:
			# garantir que o objeto conn não aponte mais para uma conexão fechada
			self.conn = None

	def is_connected(self):
		"""Retorna True se a conexão existir e estiver aberta."""
		return getattr(self, "conn", None) is not None and not self.conn.closed

	def execute(self, query):
		self.connect()
		with self.conn:
			with self.conn.cursor() as cur:
				cur.execute(query)
				return cur.fetchall()

	def __enter__(self):
		self.connect()
		return self

	def __exit__(self, exc_type, exc, tb):
		# em caso de exceção, tenta rollback; sempre fecha a conexão ao final
		if exc_type is not None and self.is_connected():
			try:
				self.conn.rollback()
			except Exception:
				pass
		self.close()
