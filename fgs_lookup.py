from proc_polystr import *
import sqlite3

class fgs_lookup:
	"""Look up places in FGS database
	@param dbloc: location of database
	
	Attributes:
		llcrnrlat: min latitude
		llcrnrlon: min longitude
		urcrnrlat: max latitude
		urcrnrlon: max longitude
		
	Functions:
		set_bounds : set min/max lat/lng
		lookup
		load_all : read all counties into fgs_dict
	"""
	def __init__(self, database):
		self.dbloc = database
		self.conn = sqlite3.connect(self.dbloc)    
		self.c = self.conn.cursor()
		orstr = " or ".join(['n{0} = :n{0}'.format(i) for i in range(1, 2)])
		self.qstring = "SELECT poly FROM county WHERE " + orstr
		self.cache = True;
		self.fgs_dict = {};
		self.llcrnrlat=-180;
		self.llcrnrlon=-180;
		self.urcrnrlat=180;
		self.urcrnrlon=180;
	
	def set_bounds(self,xmin, ymin, xmax, ymax):
		self.llcrnrlat=xmin;
		self.llcrnrlon=ymin;
		self.urcrnrlat=xmax;
		self.urcrnrlon=ymax;	
		
	def load_all(self):
		#all tables
		self.c.execute("SELECT * FROM county");
		while True:
			row = self.c.fetchone() ; 
			print(row[0], row[1])
			if row is not None:
				tmp = proc_polystr([[row[-1]]], self.llcrnrlat, self.llcrnrlon, self.urcrnrlat, self.urcrnrlon);
				if len(tmp) > 0:
					self.fgs_dict[ row[0] ] = tmp;
			else:
				break;
	
	def load_all(self):
		#all tables
		self.c.execute("SELECT * FROM county");
		while True:
			row = self.c.fetchone() ; 
			if row is not None:
				tmp = proc_polystr([[row[-1]]], self.llcrnrlat, self.llcrnrlon, self.urcrnrlat, self.urcrnrlon);
				if len(tmp) > 0:
					for t in tmp:
						if row[1] in self.fgs_dict:
							self.fgs_dict[ row[1] ].append(t);
						else:
							self.fgs_dict[ row[1] ] = [t];
			else:
				break;
					
	def lookup(self, name):
		name = name.lower();
		if self.cache and name in self.fgs_dict:
			return self.fgs_dict[name];
		else:
			self.c.execute(self.qstring, {
				'n1': name
			})
			result = self.c.fetchall();
			if( len(result) > 0 ):
				tmp = proc_polystr(result, self.llcrnrlat, self.llcrnrlon, self.urcrnrlat, self.urcrnrlon);
				if len(tmp) > 0:
					if self.cache: self.fgs_dict[name] = tmp;
					return tmp;
		return [];
		
	def destroy(self):
		self.conn.close()
