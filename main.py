from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from werkzeug.security import check_password_hash
from database import SessionLocal, init_db
from models import Quote, User
from datetime import datetime
import models



app = FastAPI(title="H's Essentials - Site")
app.add_middleware(SessionMiddleware, secret_key="scarscarscar123")

from database import SessionLocal
from models import User

db = SessionLocal()





init_db()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


WHATSAPP_NUMBER = "243978911409"

@app.get("/", response_class=HTMLResponse)
def index_redirect(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "wa_number": WHATSAPP_NUMBER,
            "year": datetime.now().year
        }
    )




@app.get("/services")
def services(request: Request):
    return templates.TemplateResponse("services.html", {"request": request, "wa_number": WHATSAPP_NUMBER})

    templates.TemplateResponse(
    "services.html",
    {
        "request": request,
        "current_year": datetime.now().year
    }
)

@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "wa_number": WHATSAPP_NUMBER})
    
    templates.TemplateResponse(
    "about.html",
    {
        "request": request,
        "current_year": datetime.now().year
    }
)

@app.get("/contact")
def contact_get(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request, "wa_number": WHATSAPP_NUMBER, "success": False})

    templates.TemplateResponse(
    "contact.html",
    {
        "request": request,
        "current_year": datetime.now().year
    }
)

@app.post("/contact")
def contact_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    # Basic validation
    if not name or not email or not message:
        raise HTTPException(status_code=400, detail="Champs obligatoires manquants")
    m = models.Message(name=name, email=email, phone=phone or "", message=message)
    db.add(m)
    db.commit()
    db.refresh(m)
    return templates.TemplateResponse("contact.html", {"request": request, "wa_number": WHATSAPP_NUMBER, "success": True})

    templates.TemplateResponse(
    "conatact.html",
    {
        "request": request,
        "current_year": datetime.now().year
    }
)

@app.get("/quote")
def quote_get(request: Request):
    return templates.TemplateResponse("quote.html", {"request": request, "wa_number": WHATSAPP_NUMBER, "success": False})

    templates.TemplateResponse(
    "quote.html",
    {
        "request": request,
        "current_year": datetime.now().year
    }
)

@app.post("/quote")
def quote_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    service: str = Form(...),
    details: str = Form(...),
    db: Session = Depends(get_db),
):
    if not name or not email or not service:
        raise HTTPException(status_code=400, detail="Champs obligatoires manquants")
    q = models.Quote(name=name, email=email, phone=phone or "", service=service, details=details)
    db.add(q)
    db.commit()
    db.refresh(q)
    return templates.TemplateResponse("quote.html", {"request": request, "wa_number": WHATSAPP_NUMBER, "success": True})

    templates.TemplateResponse(
    "quote.html",
    {
        "request": request,
        "current_year": datetime.now().year
    }
)

@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or user.password != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Utilisateur ou mot de passe incorrect"})

    # Créer la session
    request.session["user"] = user.id

    # Rediriger selon le type
    if user.is_admin:
        return RedirectResponse(url="/devis", status_code=303)
    else:
        return RedirectResponse(url="/mes-devis", status_code=303)

@app.get("/devis", response_class=HTMLResponse)
def list_devis(request: Request, db: Session = Depends(get_db)):
    # Vérification de la session
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # Récupération de l'utilisateur
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # Si admin, voir tous les devis
    if user.is_admin:
        devis = db.query(Quote).order_by(Quote.created_at.desc()).all()
    else:
        # Sinon, voir seulement ses devis
        devis = db.query(Quote).filter(Quote.user_id == user_id).order_by(Quote.created_at.desc()).all()

    return templates.TemplateResponse(
        "devis.html",
        {"request": request, "devis": devis, "user": user}
    )



@app.get("/mesdevis", response_class=HTMLResponse)
def mes_devis(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse(url="/user-login", status_code=303)

    user = db.query(User).filter(User.id == user_id, User.is_admin == False).first()
    if not user:
        return RedirectResponse(url="/user-login", status_code=303)

    devis = db.query(Quote).filter(Quote.user_id == user_id).order_by(Quote.created_at.desc()).all()
    return templates.TemplateResponse("mes_devis.html", {"request": request, "devis": devis, "user": user})


# ------------------ Inscription utilisateur ------------------
@app.get("/user-register", response_class=HTMLResponse)
def user_register_page(request: Request):
    return templates.TemplateResponse("register_user.html", {"request": request, "error": None})

@app.post("/user-register")
def user_register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),   # <-- ajouté ici
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            "register_user.html",
            {"request": request, "error": "Nom d'utilisateur déjà pris"}
        )

    new_user = User(username=username, email=email, password=password, is_admin=False)  # <-- email ajouté
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    request.session["user_id"] = new_user.id
    return RedirectResponse(url="/", status_code=303)

@app.get("/user-login", response_class=HTMLResponse)
def user_login_page(request: Request):
    return templates.TemplateResponse("login_user.html", {"request": request, "error": None})

@app.post("/user-login", response_class=HTMLResponse)
def user_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username, User.is_admin == False).first()
    if not user or user.password != password:
        return templates.TemplateResponse("login_user.html", {"request": request, "error": "Identifiants invalides"})
    
    request.session["user"] = user.id
    return RedirectResponse(url="/", status_code=303)

# ------------------ Déconnexion utilisateur ------------------
@app.get("/user-logout")
def user_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/user-login", status_code=303)



@app.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Identifiants invalides"})
    request.session["user"] = user.id
    request.session["is_admin"] = user.is_admin
    return RedirectResponse(url="/devis", status_code=303)

