from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Schema for post from customers -> using pydantic (from pydantic import BaseModel)
class PostForm(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


# Connect to an existing database
try:
    conn = psycopg2.connect(
        host="localhost",
        database="fastapi",
        user="postgres",
        password="Tuananh92",
        cursor_factory=RealDictCursor,
    )
    # Open a cursor to perform database operations
    cursor = conn.cursor()
    print("Connected to DB")
except Exception as error:
    print("Cannot Connect to DB")
    print(error)

# memory creation (for testing)
my_posts = [
    {"title": "asdfdasf", "content": "aaaa", "id": 1},
    {"title": "axcve", "content": "bbbb", "id": 2},
]


def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post


def delete_post_index(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            my_posts.pop(i)
            return True


@app.get("/")
async def wellcome():
    return {"message": "hello"}


@app.get("/posts")  # Decorator + Path, get: Retrieve data from server to browser
async def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    print(posts)
    return {"message": posts}


# this will make sure that the id we get is integer (like PostForm below)
@app.get("/posts/{id}")  # Path parameter {id} is a string
async def get_post(id: int):
    cursor.execute(
        """SELECT * FROM posts WHERE id = %s""",
        (str(id)),
    )
    postFetch = cursor.fetchone()
    print(postFetch)
    if not postFetch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
        # response.status_code = status.HTTP_404_NOT_FOUND
    return {"message": postFetch}


# Get Post Message and put into a pydantic format (Post) which name is "new_post"
@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(new_post: PostForm):

    # This is for state change
    cursor.execute(
        """INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING * """,
        (new_post.title, new_post.content, new_post.published),
    )
    newPostFetch = cursor.fetchone()

    # this is for commiting the state change into DB (anytime we change sth in the DB)
    conn.commit()

    return {"message": newPostFetch}


# when we delete a post, we dont want to return anything, hence only return Response(status_code)
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    cursor.execute(
        """DELETE FROM posts WHERE id = %s RETURNING * """,
        (str(id)),
    )
    deletePost = cursor.fetchone()
    conn.commit()
    if deletePost == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )

    # We dont return anything for delete post
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
async def update_post(id: int, update_post: PostForm):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
        (update_post.title, update_post.content, update_post.published, str(id)),
    )
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    return {"data": updated_post}
