#include "solvespace.h"

#include "harness.h"

// A new extrude group used to start 200 screen pixels deep along the view
// direction, so its depth depended on the zoom and the view angle at the moment
// it was created. It now starts from the sketch: half the sketch's largest
// dimension, along the workplane normal. Whatever the view, the same sketch must
// give the same starting extrusion.
TEST_CASE(zoom_independent) {
    CHECK_LOAD("normal.slvs");

    Group *ext = NULL;
    for(Group &g : SK.group) {
        if(g.type == Group::Type::EXTRUDE) { ext = &g; break; }
    }
    CHECK_TRUE(ext != NULL);

    Entity *wp = SK.GetEntity(ext->predef.entityB);
    Vector n = SK.GetEntity(wp->normal)->NormalN();

    // A close view and a far one, looking from the same side of the plane.
    Vector nearView = n.WithMagnitude(0.5);
    Vector farView  = n.WithMagnitude(5000);
    Vector a = ext->DefaultExtrusion(nearView);
    Vector b = ext->DefaultExtrusion(farView);
    CHECK_TRUE(a.Equals(b));

    // Along the workplane normal, and a real depth rather than a sliver.
    CHECK_TRUE(a.Cross(n).Magnitude() < LENGTH_EPS);
    CHECK_TRUE(a.Magnitude() > 1.0);

    // Looking from the other side flips the side the part grows on, not its depth.
    Vector c = ext->DefaultExtrusion(n.ScaledBy(-1));
    CHECK_TRUE(c.Equals(a.ScaledBy(-1)));
}
