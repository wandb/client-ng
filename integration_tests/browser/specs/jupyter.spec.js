describe("Jupyter Notebook", () => {
  it("Should be able to log images and scalars", () => {
    visit("http://localhost:8890/notebooks/image_test.ipynb");
  });
});
