from fastapi import FastAPI, Depends
from moduels import Product as product
from fastapi.middleware.cors import CORSMiddleware
from database import session, engine
import database_modules
from sqlalchemy.orm import Session
import mangum


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)
database_modules.Base.metadata.create_all(bind=engine)

products = [
    product(id=1, name="Laptop", description="gaming laptop", price=1500.0, quantity=10),
    product(id=2, name="Mouse", description="wireless mouse", price=25.0, quantity=50),
    product(id=3, name="Keyboard", description="mechanical keyboard", price=100.0, quantity=20),
    product(id=4, name="Monitor", description="4K monitor", price=400.0, quantity=15)
]

def init_db():
    db = session()
    count = db.query(database_modules.Product).count

    if count == 0:
        for product in products:
            db.add(database_modules.Product(**product.model_dump()))

        db.commit()

init_db( )


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home(): 
    return "welcome home boys"





@app.get ("/products")
def get_all_products(db:Session = Depends(get_db)):
    db_products = db.query(database_modules.Product).all()
    
    return db_products

@app.get("/products/{id}")
def get_prod_by_id(id: int,db:Session = Depends(get_db)):
    db_product = db.query(database_modules.Product).filter(database_modules.Product.id == id).first()
    if db_product :
        return db_product
    return {"error" : f"no product found with this id number {id} please try again with another id number"}
    


@app.post("/products")
def add_product (product: product, db:Session = Depends(get_db)):
   db.add(database_modules.Product(**product.model_dump()))
   db.commit()  
   return product

@app.put("/products/{id}")
def update_the_product(id:int, product: product, db:Session = Depends(get_db) ):
    db_product = db.query(database_modules.Product).filter(database_modules.Product.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        db.refresh(db_product)
        return "product is updated successfully"
    else:
        return {"error": f"No product found with id {id} to update."}
    
  

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_modules.Product).filter(database_modules.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "product is deleted successfully"
    else:
        return {"error": f"No product found with id {id} to delete."}
handler = mangum.Mangum(app)