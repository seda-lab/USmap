from proc_polystr import *	
import sqlite3

class gadm_lookup:
	"""Look up places in GADM database
	@param dbloc: location of database
	@param use_biggest: when multiple polygons define an area, only use the largest (useful to exclude islands)
	@param tolerance: Smooth polygons
	
	Attributes:
		llcrnrlat: min latitude
		llcrnrlon: min longitude
		urcrnrlat: max latitude
		urcrnrlon: max longitude
		
	Functions:
		set_bounds : set min/max lat/lng
		lookup
	"""
	def __init__(self, database, use_biggest=False, tolerance=0):
		self.dbloc = database
		self.conn = sqlite3.connect(self.dbloc)    
		self.c = self.conn.cursor()
		orstr = " or ".join(['n{0} = :n{0}'.format(i) for i in range(0, 6)])
		self.qstring = "SELECT poly FROM gadm WHERE " + orstr
		self.cache = True;

		self.gadm_dict = {};
		self.llcrnrlat=-180;
		self.llcrnrlon=-180;
		self.urcrnrlat=180;
		self.urcrnrlon=180;
		self.use_biggest=use_biggest;
		self.tolerance = tolerance;
	
	def set_bounds(self,xmin, ymin, xmax, ymax):
		self.llcrnrlat=xmin;
		self.llcrnrlon=ymin;
		self.urcrnrlat=xmax;
		self.urcrnrlon=ymax;	
		
			
	def load_all_nx_names(self, n=1):
		#all tables
		self.c.execute("SELECT * FROM gadm");
		names = set();
		while True:
			row = self.c.fetchone() ; 
			if row is not None:
				names.add(row[n])
			else:
				break;
		return names;
		
		
	def lookup(self, name, level=-1):
		name = name.lower()
		if self.cache and name in self.gadm_dict:
			return self.gadm_dict[name];
		else:
			if level == -1:
				self.c.execute(self.qstring, {
					'n0' : name, 'n1': name , 'n2': name, 'n3': name, 'n4': name, 'n5': name,
				})
			else:
				self.c.execute("SELECT poly FROM gadm WHERE n"+str(level)+" = :n"+str(level), {
					'n'+str(level) : name
				})
			result = self.c.fetchall();
			if( len(result) > 0 ):
				tmp = proc_polystr(result, self.llcrnrlat, self.llcrnrlon, self.urcrnrlat, self.urcrnrlon, self.tolerance);
				if len(tmp) > 1:
					if self.use_biggest: 
						tmp = [ max(tmp, key=lambda x: x.area) ];
					if self.cache: self.gadm_dict[name] = tmp;
					return tmp;
					
				return tmp;
		return [];
		
	def destroy(self):
		self.conn.close()
