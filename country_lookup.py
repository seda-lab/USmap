from proc_polystr import *	
import sqlite3

class country_lookup:
	"""Look up places in country database
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
		self.qstring = "SELECT poly FROM country WHERE name = :name"

		self.cache = True;
		self.country_dict = {};
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
		
			
	def load_all_names(self):
		#all tables
		self.c.execute("SELECT * FROM country");
		names = [];
		while True:
			row = self.c.fetchone() ; 
			if row is not None:
				names.append(row[0])
			else:
				break;
		return names;
		
	def lookup(self, name):
		name = name.lower()
		if self.cache and name in self.country_dict:
			return self.country_dict[name];
		else:
			self.c.execute(self.qstring, {
				'name': name 
			})
			result = self.c.fetchall();

			if( len(result) > 0 ):
				tmp = proc_polystr(result, self.llcrnrlat, self.llcrnrlon, self.urcrnrlat, self.urcrnrlon, self.tolerance);
				if len(tmp) > 1:
					if self.use_biggest: 
						tmp = [ sorted(tmp, key=lambda x: x.area, reverse=True)[0] ];
					if self.cache: self.country_dict[name] = tmp;
					return tmp;
					
				return tmp;
		return [];
		
	def destroy(self):
		self.conn.close()

if __name__ == "__main__":
	
	country = country_lookup("country.db");
	country.lookup("France")
