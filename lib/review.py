from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id
        

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        if not isinstance(year, int):
            raise ValueError("Property year must be assigned an int")
        if year < 2000:
            raise ValueError("Property year must be greater than or equal to 2000")
        if not summary or len(summary) == 0:
            raise ValueError("Summary must have a length greater than 0")
        if not isinstance(employee_id, int):
            raise ValueError("id not in employees table")
        
        sql = "SELECT id FROM employees WHERE id = ?"
        result = CURSOR.execute(sql, (employee_id,)).fetchone()

        if result is None:
            raise ValueError(f"Employee with id {employee_id} does not exist")

        review = cls(year, summary, employee_id)
        review.save()
    
        return review
    @property
    def employee_id(self):
        """Getter for employee_id"""
        return self._employee_id

    @employee_id.setter
    def employee_id(self, new_employee_id):
        """Setter for employee_id that checks if the employee exists in the database."""
        sql = "SELECT id FROM employees WHERE id = ?"
        result = CURSOR.execute(sql, (new_employee_id,)).fetchone()
        if result is None:
            raise ValueError(f"Employee with id {new_employee_id} does not exist")
        self._employee_id = new_employee_id

    
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        review = cls(row[1], row[2], row[3])  
        review.id = row[0]
        cls.all[review.id] = review  
        return review
   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    # def validate_property_year(self, employee_id):
    #     if not isinstance(employee_id, int):  # Check if value is NOT an integer
    #         raise ValueError("Property year must be assigned an int")
    #     # else:
    #     #  print("this century", "Excellent work ethic! Outstanding programming skills!")

