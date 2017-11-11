package com.grazianomarallo.RestfulService;

public class Cafeteria extends Resource {
    private String[] menu;

    public Cafeteria(int capacity, int busyLevel, BaseInfo informations) {
        super(capacity, informations);
    }
    public String[] getMenu() {
        return menu;
    }

    public void setMenu(String[] menu) {
        this.menu = menu;
    }

}
