from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

# Schema for post from customers -> using pydantic (from pydantic import BaseModel)
class PostForm(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


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
    return {"message": my_posts}


# this will make sure that the id we get is integer (like PostForm below)
@app.get("/posts/{id}")  # Path parameter {id} is a string
async def get_post(id: int):
    print(id)
    if not find_post(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
        # response.status_code = status.HTTP_404_NOT_FOUND
    return {"message": f"Here is the post you are looking for: {find_post(id)}"}


# Get Post Message and put into a pydantic format (Post) which name is "new_post"
@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(new_post: PostForm):
    print(new_post.title)
    print(new_post.content)
    print(new_post.published)
    print(new_post.rating)
    print(new_post.dict())
    postDict = new_post.dict()
    postDict["id"] = randrange(0, 1000000)  # add random ID to PostForm
    my_posts.append(postDict)
    return {"message": postDict}


# when we delete a post, we dont want to return anything, hence only return Response(status_code)
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    print(id)
    if delete_post_index(id) != True:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    delete_post_index(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
async def update_post(id: int, new_post: PostForm):
    postDict = new_post.dict()
    postDict["id"] = id  # add id key to post dictionary
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            my_posts[i] = postDict
            return {"data": postDict}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "not found your request"},
            )
